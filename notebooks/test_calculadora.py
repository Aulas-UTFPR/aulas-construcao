from calculadora import Calculadora

def test_soma():
    calc = Calculadora()
    assert calc.soma(2, 3) == 5

def test_subtrai():
    calc = Calculadora()
    assert calc.subtrai(10, 4) == 6

def test_multiplica():
    calc = Calculadora()
    assert calc.multiplica(2, 3) == 6

def test_divide():
    calc = Calculadora()
    assert calc.divide(10, 2) == 5.0
