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


def calcular_envio(pedido):
    if pedido["zona"] not in TARIFAS:
        raise ValueError("zona desconocida: " + str(pedido["zona"]))
    base, por_kilo, por_kilo_extra, factor_express = TARIFAS[pedido["zona"]]
    total = _tarifa_por_peso(base, por_kilo, por_kilo_extra, pedido["peso"])
    if pedido["express"]:
        total = total * factor_express
    if pedido["cliente"] == "frecuente":
        if total > 30000:
            total = total - total * 0.1
        else:
            total = total - total * 0.05
    total = round(total / 100) * 100
    return total


def factura(pedido):
    total = calcular_envio(pedido)
    if pedido["cliente"] == "frecuente":
        linea = "Envío " + pedido["zona"] + (" express" if pedido["express"] else "") + " (cliente frecuente): $" + "{:,}".format(int(total)).replace(",", ".")
    else:
        linea = "Envío " + pedido["zona"] + (" express" if pedido["express"] else "") + ": $" + "{:,}".format(int(total)).replace(",", ".")
    iva = round(total * 0.19 / 100) * 100
    linea2 = "IVA (19 %): $" + "{:,}".format(int(iva)).replace(",", ".")
    linea3 = "Total: $" + "{:,}".format(int(total + iva)).replace(",", ".")
    return linea + "\n" + linea2 + "\n" + linea3
