# Módulo heredado del sistema de envíos. Funciona y está en producción.
# Nadie quiere tocarlo: cada cambio de tarifa toma días y rompe algo.


def calcular_envio(pedido):
    total = 0
    if pedido["zona"] == "urbana":
        if pedido["peso"] <= 1:
            total = 8000
        else:
            if pedido["peso"] <= 5:
                total = 8000 + (pedido["peso"] - 1) * 1500
            else:
                total = 8000 + 4 * 1500 + (pedido["peso"] - 5) * 2500
        if pedido["express"]:
            total = total * 1.5
    elif pedido["zona"] == "regional":
        if pedido["peso"] <= 1:
            total = 12000
        else:
            if pedido["peso"] <= 5:
                total = 12000 + (pedido["peso"] - 1) * 2000
            else:
                total = 12000 + 4 * 2000 + (pedido["peso"] - 5) * 3000
        if pedido["express"]:
            total = total * 1.5
    elif pedido["zona"] == "nacional":
        if pedido["peso"] <= 1:
            total = 18000
        else:
            if pedido["peso"] <= 5:
                total = 18000 + (pedido["peso"] - 1) * 2500
            else:
                total = 18000 + 4 * 2500 + (pedido["peso"] - 5) * 4000
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
