# GCMS S4 — Estrategias de Mantenimiento y Evolución

Material de la **Sesión 4** del curso *Gestión de Configuración y Mantenimiento de Software* (GCMS),
Unidad 4: **Estrategias de mantenimiento y evolución**. Maestría en Ingeniería de Software,
Universidad de La Sabana.

Es la unidad que cierra el proyecto del curso. Cada grupo:

- elige mejoras para su sistema a partir del diagnóstico de la Unidad 1;
- las implementa con el pipeline de la Unidad 3 como red de seguridad;
- demuestra con mediciones del antes y el después que el sistema mejoró;
- presenta el proyecto completo.

Las actividades de la unidad:

- **Actividad 4. Propuesta e implementación de estrategias de mantenimiento y evolución** · grupal, de 2
  a 3 · **25 %** · 20 horas.
  - **Entregables:**
    - un documento técnico de **8 a 10 páginas** o un **README.md**;
    - el código o las evidencias de la implementación;
    - los resultados de la mejora: el antes y el después.
- **Actividad 5. Presentación final del proyecto** · grupal · **10 %** · 10 horas.
  - **Entregables:**
    - una presentación de **10 a 15 diapositivas**;
    - una demo funcional;
    - un resumen ejecutivo de **2 a 3 páginas** o README.md.
- Las dos se califican con las rúbricas del aula.
- **Los formatos F-22 a F-28 no se suben.**

---

## Empiecen aquí

**Todo el material se abre desde aquí, sin descargar nada:**
<https://cesaravegaf312.github.io/GCMS-S4_Estrategias_de_Mantenimiento/>

1. **Lean el [enunciado](documentos/1_actividades/GCMS_S4_Enunciado_Actividades_4_y_5.pdf).**
2. **Recorran el [ejercicio de refactorización](ejercicio/)** y su historial, o el
   [interactivo](interactivos/refactorizacion_interactivo.html), que muestra el código de cada paso.
3. **Lean el [recorrido resuelto](documentos/2_ejemplo/GCMS_S4_Recorrido_Resuelto.pdf).**
4. **Midan el antes** de su sistema **antes de tocarlo** y llenen los
   [Instrumentos F-22 a F-28](documentos/3_como_se_hace/GCMS_S4_Instrumentos.pdf).

---

## El ejercicio de refactorización

La carpeta [`ejercicio/`](ejercicio/) contiene `envios/tarifas.py`, un módulo heredado de tarifas de envío,
y 24 pruebas de caracterización en `tests/`. El historial de este repositorio muestra la refactorización
en cuatro pasos, un commit cada uno:

| Paso | Commit | Complejidad máxima | Líneas duplicadas |
|---|---|---|---|
| Código heredado y pruebas de caracterización | `5e6bf7c` | 15 | 8 |
| Extrae el cálculo por peso que se repetía en las tres zonas | `06216a6` | 9 | 6 |
| Reemplaza los condicionales por zona con una tabla de tarifas | `8f1e225` | 5 | 0 |
| Extrae el descuento por cliente y el redondeo a centenas | `d51f577` | 4 | 0 |
| Elimina la duplicación del formato de la factura | `3f2ee8f` | 3 | 0 |

El flujo [`.github/workflows/ejercicio.yml`](.github/workflows/ejercicio.yml) corre las pruebas en cada
PR que toque el ejercicio. También escribe el impacto del último commit en el resumen de la ejecución.
Las cinco ejecuciones de los pasos están en verde, en la pestaña **Actions**.

Para practicar, vuelvan al código heredado y refactoricen por su cuenta:

```bash
git switch --detach 5e6bf7c
cd ejercicio && pytest -q
```

Al escribir las pruebas de caracterización apareció una rareza: un envío urbano de 1,3 kg cuesta 8.450 y
el módulo lo cobra 8.400, porque `round()` de Python lleva los .5 al número par. La refactorización la
conserva, porque corregirla cambia el comportamiento. Queda como deuda, y es un buen ejercicio para hacer
en un commit propio.

---

## La herramienta de impacto

`herramientas/impacto.py` compara el código de Python en dos versiones de un repositorio Git, sin
ejecutarlo. Mide:

- líneas de código y funciones;
- complejidad ciclomática total, máxima y promedio;
- anidamiento máximo;
- funciones largas y funciones complejas;
- líneas duplicadas;
- funciones de prueba.

Escribe `impacto_funciones.csv` con el detalle por función. Requiere **Python 3.8 o posterior** y **git**,
sin bibliotecas externas.

```bash
git tag -a antes-de-mejoras -m "Línea base de medición"      # antes de tocar el código
python herramientas/impacto.py <sistema> --antes antes-de-mejoras --despues HEAD --ruta src --pruebas tests
```

Las métricas no prueban que el comportamiento se conservó: eso lo prueban las pruebas, en el pipeline.
Tampoco reemplazan al objetivo de la mejora. Medida con esta herramienta, la reestructuración de Flask
3.0 bajó su complejidad máxima de 30 a 23 y subió su duplicación de 477 a 775 líneas, porque su objetivo
era otro: separar el núcleo de la entrada y salida.

---

## Estructura del repositorio

```text
GCMS-S4_Estrategias_de_Mantenimiento/
├── index.html          ← portada: abre desde aquí todo lo demás
├── presentacion.html   ← las 20 diapositivas de la sesión
├── README.md
├── LICENSE
├── ejercicio/          ← módulo heredado, pruebas de caracterización e historial de la refactorización
├── .github/workflows/  ← la CI del ejercicio
├── documentos/         ← enunciado, recorrido resuelto, instrumentos y diapositivas (PDF)
├── interactivos/       ← refactorización paso a paso y ¿reemplazar o evolucionar?
├── herramientas/       ← impacto.py
├── ejemplo_flask/      ← el detalle por función de Flask 2.3.3 y 3.0.0
└── fuentes/            ← fuentes HTML de los PDF y el script para regenerarlos
```

### Recursos interactivos — carpeta `interactivos/`

| Archivo | Descripción |
|---|---|
| [`refactorizacion_interactivo.html`](interactivos/refactorizacion_interactivo.html) | El código de cada commit del ejercicio, con sus métricas comparadas con las del código heredado y su ejecución de la CI. |
| [`reemplazar_o_evolucionar_interactivo.html`](interactivos/reemplazar_o_evolucionar_interactivo.html) | Ocho preguntas sobre el sistema del grupo. Cada respuesta inclina la balanza entre refactorizar, modernizar por partes o reemplazar, y deja escrita la razón. |

---

## Material de la unidad

**Obligatorio**

- Fowler, M. (2018). *Refactoring: Improving the design of existing code* (2.ª ed.). Addison-Wesley. Capítulos 1 y 2.
- Beyer, B., Jones, C., Petoff, J., & Murphy, N. R. (2016). *Site reliability engineering*. O'Reilly Media. Capítulos 1 a 3.
- ISO/IEC/IEEE. (2022). *ISO/IEC/IEEE 14764:2022 Software engineering — Software life cycle processes — Maintenance*.

**Complementario**

- Prometheus. *Documentation*. https://prometheus.io/docs/
- Grafana Labs. *Grafana documentation*. https://grafana.com/docs/

---

## Para el docente: regenerar los PDF

```bash
node fuentes/imprimir_pdf.js   # los cuatro PDF; requiere Playwright con Chromium
```

---

## Referencias de la sesión

- Beyer, B., Jones, C., Petoff, J., & Murphy, N. R. (2016). *Site reliability engineering: How Google runs production systems*. O'Reilly Media.
- Feathers, M. (2004). *Working effectively with legacy code*. Prentice Hall.
- Fowler, M. (2004). *Strangler fig application*. https://martinfowler.com/bliki/StranglerFigApplication.html
- Fowler, M. (2018). *Refactoring: Improving the design of existing code* (2.ª ed.). Addison-Wesley.
- ISO/IEC/IEEE. (2022). *ISO/IEC/IEEE 14764:2022 Software engineering — Software life cycle processes — Maintenance*.
- Parnas, D. L. (1994). Software aging. En *Proceedings of the 16th International Conference on Software Engineering* (pp. 279–287). IEEE.

---

## Licencia

Este material se publica bajo la licencia
**[Creative Commons Atribución-NoComercial-CompartirIgual 4.0 Internacional (CC BY-NC-SA 4.0)](https://creativecommons.org/licenses/by-nc-sa/4.0/deed.es)**.
Ver [`LICENSE`](LICENSE).

*Los datos de los ejemplos provienen del repositorio público de [Flask](https://github.com/pallets/flask),
proyecto de Pallets con licencia BSD-3-Clause.*
