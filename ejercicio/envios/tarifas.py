# Módulo de tarifas del sistema de envíos. Cambiar una tarifa es cambiar una fila de la tabla.

# zona: (primer kilo, por kilo de 1 a 5, por kilo desde 5, factor express)
TARIFAS = {
    "urbana": (8000, 1500, 2500, 1.5),
    "regional": (12000, 2000, 3000, 1.5),
    "nacional": (18000, 2500, 4000, 1.8),
}


def _tarifa_por_peso(base, por_kilo, por_kilo_extra, peso):
    # Primer kilo a precio base, de 1 a 5 kilos un valor por kilo, y de ahí en adelante otro.
    if peso <= 1:
        return base
    if peso <= 5:
        return base + (peso - 1) * por_kilo
    return base + 4 * por_kilo + (peso - 5) * por_kilo_extra


def _con_descuento(total, cliente):
    # Clientes frecuentes: 10 % por encima de 30.000 y 5 % hasta 30.000.
    if cliente != "frecuente":
        return total
    return total * (0.9 if total > 30000 else 0.95)


def redondear_centenas(valor):
    # Conserva el redondeo heredado: round() lleva los .5 al par (8.450 queda en 8.400).
    # No se corrige aquí porque cambiaría el comportamiento: está registrado como deuda.
    return round(valor / 100) * 100


def calcular_envio(pedido):
    if pedido["zona"] not in TARIFAS:
        raise ValueError("zona desconocida: " + str(pedido["zona"]))
    base, por_kilo, por_kilo_extra, factor_express = TARIFAS[pedido["zona"]]
    total = _tarifa_por_peso(base, por_kilo, por_kilo_extra, pedido["peso"])
    if pedido["express"]:
        total = total * factor_express
    return redondear_centenas(_con_descuento(total, pedido["cliente"]))


def _pesos(valor):
    # 47600 → "$47.600"
    return "$" + f"{int(valor):,}".replace(",", ".")


def _descripcion(pedido):
    express = " express" if pedido["express"] else ""
    frecuente = " (cliente frecuente)" if pedido["cliente"] == "frecuente" else ""
    return f"Envío {pedido['zona']}{express}{frecuente}"


def factura(pedido):
    total = calcular_envio(pedido)
    iva = redondear_centenas(total * 0.19)
    return "\n".join([
        f"{_descripcion(pedido)}: {_pesos(total)}",
        f"IVA (19 %): {_pesos(iva)}",
        f"Total: {_pesos(total + iva)}",
    ])
