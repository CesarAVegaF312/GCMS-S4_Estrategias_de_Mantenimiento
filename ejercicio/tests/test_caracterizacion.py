"""Pruebas de caracterización: fijan lo que el módulo hace hoy, no lo que debería hacer.

Se escriben antes de refactorizar. Si una refactorización cambia alguno de estos resultados, no fue una
refactorización: cambió el comportamiento.
"""

import pytest

from envios.tarifas import calcular_envio, factura


def pedido(zona="urbana", peso=1, express=False, cliente="nuevo"):
    return {"zona": zona, "peso": peso, "express": express, "cliente": cliente}


@pytest.mark.parametrize(
    ("zona", "peso", "esperado"),
    [
        ("urbana", 1, 8000), ("urbana", 3, 11000), ("urbana", 5, 14000), ("urbana", 8, 21500),
        ("regional", 1, 12000), ("regional", 3, 16000), ("regional", 5, 20000), ("regional", 8, 29000),
        ("nacional", 1, 18000), ("nacional", 3, 23000), ("nacional", 5, 28000), ("nacional", 8, 40000),
        ("urbana", 0.5, 8000), ("regional", 2.5, 15000),
    ],
)
def test_tarifa_base(zona, peso, esperado):
    assert calcular_envio(pedido(zona, peso)) == esperado


@pytest.mark.parametrize(
    ("zona", "esperado"),
    [("urbana", 21000), ("regional", 30000), ("nacional", 50400)],
)
def test_express(zona, esperado):
    assert calcular_envio(pedido(zona, 5, express=True)) == esperado


@pytest.mark.parametrize(
    ("zona", "peso", "express", "esperado"),
    [
        ("urbana", 1, False, 7600),       # 5 % por debajo de 30.000
        ("nacional", 8, False, 36000),    # 10 % por encima de 30.000
        ("regional", 5, True, 28500),     # justo 30.000: aplica el 5 %
    ],
)
def test_cliente_frecuente(zona, peso, express, esperado):
    assert calcular_envio(pedido(zona, peso, express, "frecuente")) == esperado


def test_redondeo_a_centenas():
    # 8.450 se vuelve 8.400, no 8.500: round() de Python lleva los .5 al número par.
    # Es un comportamiento heredado; la refactorización lo conserva y se registra como deuda (F-22).
    assert calcular_envio(pedido("urbana", 1.3)) == 8400


def test_zona_desconocida():
    with pytest.raises(ValueError, match="zona desconocida: rural"):
        calcular_envio(pedido("rural"))


def test_factura_cliente_nuevo():
    assert factura(pedido("nacional", 8)) == (
        "Envío nacional: $40.000\nIVA (19 %): $7.600\nTotal: $47.600"
    )


def test_factura_cliente_frecuente_express():
    # 21.000 menos 5 % es 19.950, que redondeado a centenas queda en 20.000.
    assert factura(pedido("urbana", 5, True, "frecuente")) == (
        "Envío urbana express (cliente frecuente): $20.000\nIVA (19 %): $3.800\nTotal: $23.800"
    )
