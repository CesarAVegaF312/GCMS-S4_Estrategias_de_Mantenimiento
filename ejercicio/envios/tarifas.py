# Módulo heredado del sistema de envíos. Funciona y está en producción.
# Nadie quiere tocarlo: cada cambio de tarifa toma días y rompe algo.


def _tarifa_por_peso(base, por_kilo, por_kilo_extra, peso):
    # Primer kilo a precio base, de 1 a 5 kilos un valor por kilo, y de ahí en adelante otro.
    if peso <= 1:
        return base
    if peso <= 5:
        return base + (peso - 1) * por_kilo
    return base + 4 * por_kilo + (peso - 5) * por_kilo_extra


def calcular_envio(pedido):
    total = 0
    if pedido["zona"] == "urbana":
        total = _tarifa_por_peso(8000, 1500, 2500, pedido["peso"])
        if pedido["express"]:
            total = total * 1.5
    elif pedido["zona"] == "regional":
        total = _tarifa_por_peso(12000, 2000, 3000, pedido["peso"])
        if pedido["express"]:
            total = total * 1.5
    elif pedido["zona"] == "nacional":
        total = _tarifa_por_peso(18000, 2500, 4000, pedido["peso"])
        if pedido["express"]:
            total = total * 1.8
    else:
        raise ValueError("zona desconocida: " + str(pedido["zona"]))
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
