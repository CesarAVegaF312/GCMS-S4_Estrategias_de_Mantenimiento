#!/usr/bin/env python3
"""Mide el impacto de una mejora comparando el código de Python en dos versiones de un repositorio Git.

Material de la Unidad 4 de GCMS (Gestión de Configuración y Mantenimiento de Software).
Alimenta los formatos F-25 y F-26. Para cada versión calcula, sin ejecutar el código:

  - líneas de código (sin líneas en blanco ni comentarios) y número de funciones;
  - complejidad ciclomática de cada función (1 + puntos de decisión) y su anidamiento máximo;
  - funciones largas (más de 25 líneas) y funciones complejas (complejidad mayor que 10);
  - líneas duplicadas: bloques de 3 líneas normalizadas que aparecen más de una vez;
  - número de pruebas (funciones test_*) en la ruta de pruebas.

Escribe impacto_funciones.csv con el detalle por función en las dos versiones.
Solo usa la biblioteca estándar de Python 3.8 o posterior y git.

Uso:
  python impacto.py RUTA_DEL_REPOSITORIO --antes REF --despues REF --ruta src/paquete [--pruebas tests]
"""

import argparse
import ast
import csv
import re
import subprocess
import sys
from collections import Counter
from pathlib import Path

DECISIONES = (ast.If, ast.For, ast.AsyncFor, ast.While, ast.IfExp, ast.ExceptHandler, ast.Assert, ast.comprehension)
LARGA, COMPLEJA, VENTANA = 25, 10, 3


def git(repo, *args):
    r = subprocess.run(["git", "-C", str(repo), *args], check=False, capture_output=True, text=True,
                       encoding="utf-8", errors="replace")
    if r.returncode != 0:
        sys.exit(f"Falló: git {' '.join(args)}\n{r.stderr.strip()}")
    return r.stdout


def archivos(repo, ref, ruta):
    salida = git(repo, "ls-tree", "-r", "--name-only", ref, "--", ruta)
    return {a: git(repo, "show", f"{ref}:{a}") for a in salida.splitlines() if a.endswith(".py")}


def complejidad(nodo):
    total = 1
    for hijo in ast.walk(nodo):
        if isinstance(hijo, DECISIONES):
            total += 1 + (len(hijo.ifs) if isinstance(hijo, ast.comprehension) else 0)
        elif isinstance(hijo, ast.BoolOp):
            total += len(hijo.values) - 1
        elif hasattr(ast, "match_case") and isinstance(hijo, ast.match_case):
            total += 1
    return total


def anidamiento(nodo, nivel=0):
    bloques = (ast.If, ast.For, ast.AsyncFor, ast.While, ast.With, ast.AsyncWith, ast.Try)
    maximo = nivel
    for hijo in ast.iter_child_nodes(nodo):
        if isinstance(hijo, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)):
            continue
        siguiente = nivel + 1 if isinstance(hijo, bloques) else nivel
        maximo = max(maximo, anidamiento(hijo, siguiente))
    return maximo


def lineas_codigo(texto):
    return [linea.strip() for linea in texto.splitlines() if linea.strip() and not linea.strip().startswith("#")]


def funciones(nombre, texto):
    try:
        arbol = ast.parse(texto)
    except SyntaxError:
        return []
    filas = []
    for nodo in ast.walk(arbol):
        if isinstance(nodo, (ast.FunctionDef, ast.AsyncFunctionDef)):
            lineas = (nodo.end_lineno or nodo.lineno) - nodo.lineno + 1
            filas.append({"archivo": nombre, "funcion": nodo.name, "lineas": lineas,
                          "complejidad": complejidad(nodo), "anidamiento": anidamiento(nodo)})
    return filas


def duplicadas(textos):
    """Líneas que pertenecen a bloques de VENTANA líneas normalizadas repetidos en algún lugar del código."""
    normal = lambda l: re.sub(r"\s+", " ", re.sub(r"(['\"]).*?\1", "S", l))  # noqa: E731
    vistos, posiciones = Counter(), []
    for nombre, texto in textos.items():
        lineas = [normal(l) for l in lineas_codigo(texto)]
        for i in range(len(lineas) - VENTANA + 1):
            bloque = tuple(lineas[i:i + VENTANA])
            if all(len(x) > 3 for x in bloque):
                vistos[bloque] += 1
                posiciones.append((nombre, i, bloque))
    repetidas = set()
    for nombre, i, bloque in posiciones:
        if vistos[bloque] > 1:
            repetidas.update((nombre, i + k) for k in range(VENTANA))
    return len(repetidas)


def medir(repo, ref, ruta, ruta_pruebas):
    textos = archivos(repo, ref, ruta)
    fs = [f for nombre, texto in textos.items() for f in funciones(nombre, texto)]
    pruebas = 0
    if ruta_pruebas:
        for texto in archivos(repo, ref, ruta_pruebas).values():
            pruebas += len(re.findall(r"^\s*def test_", texto, re.M))
    comp = [f["complejidad"] for f in fs]
    peor = max(fs, key=lambda f: f["complejidad"]) if fs else None
    return {
        "archivos": len(textos),
        "líneas de código": sum(len(lineas_codigo(t)) for t in textos.values()),
        "funciones": len(fs),
        "complejidad total": sum(comp),
        "complejidad máxima": max(comp) if comp else 0,
        "complejidad promedio": round(sum(comp) / len(comp), 1) if comp else 0,
        "anidamiento máximo": max((f["anidamiento"] for f in fs), default=0),
        f"funciones de más de {LARGA} líneas": sum(1 for f in fs if f["lineas"] > LARGA),
        f"funciones con complejidad > {COMPLEJA}": sum(1 for c in comp if c > COMPLEJA),
        "líneas duplicadas": duplicadas(textos),
        "funciones de prueba": pruebas,
        "_peor": f"{peor['funcion']} ({peor['complejidad']})" if peor else "",
        "_detalle": fs,
    }


def main():
    p = argparse.ArgumentParser(description="Compara métricas de código de Python entre dos versiones de un repositorio.")
    p.add_argument("repo")
    p.add_argument("--antes", required=True, help="versión de partida (etiqueta, rama o commit)")
    p.add_argument("--despues", required=True, help="versión mejorada (etiqueta, rama o commit)")
    p.add_argument("--ruta", required=True, help="carpeta o archivo del código que se mide")
    p.add_argument("--pruebas", default="", help="carpeta de las pruebas (opcional)")
    p.add_argument("--salida", default=".")
    a = p.parse_args()
    repo = Path(a.repo).resolve()

    antes = medir(repo, a.antes, a.ruta, a.pruebas)
    despues = medir(repo, a.despues, a.ruta, a.pruebas)

    print(f"{'Métrica':<36}{'Antes':>10}{'Después':>10}{'Cambio':>10}")
    for clave, valor in antes.items():
        if clave.startswith("_"):
            continue
        nuevo = despues[clave]
        cambio = nuevo - valor
        print(f"{clave:<36}{valor:>10}{nuevo:>10}{cambio:>+10.1f}" if isinstance(cambio, float)
              else f"{clave:<36}{valor:>10}{nuevo:>10}{cambio:>+10}")
    print(f"\nFunción más compleja antes: {antes['_peor']} · después: {despues['_peor']}")

    salida = Path(a.salida)
    salida.mkdir(parents=True, exist_ok=True)
    with open(salida / "impacto_funciones.csv", "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=["version", "archivo", "funcion", "lineas", "complejidad", "anidamiento"])
        w.writeheader()
        for version, datos in (("antes", antes), ("despues", despues)):
            for fila in datos["_detalle"]:
                w.writerow({"version": version, **fila})
    print(f"Detalle por función en {salida / 'impacto_funciones.csv'}")
    print("\nEstas métricas no prueban que el comportamiento se conservó: eso lo prueban las pruebas, en el pipeline.")


if __name__ == "__main__":
    main()
