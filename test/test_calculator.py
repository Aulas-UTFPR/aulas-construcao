import sys
import os

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from calculator.calculator import Calculator

def test_add():
    calc = Calculator()
    assert calc.add(2, 3) == 5
    assert calc.add(-2, 3) == 1
    assert calc.add(0, 0) == 0

def test_subtract():
    calc = Calculator()
    assert calc.subtract(5, 3) == 2
    assert calc.subtract(0, 3) == -3
    assert calc.subtract(-3, -3) == 0

def test_multiply():
    calc = Calculator()
    assert calc.multiply(4, 3) == 12
    assert calc.multiply(-4, 3) == -12
    assert calc.multiply(0, 3) == 0

def test_divide():
    calc = Calculator()
    assert calc.divide(10, 2) == 5
    assert calc.divide(-10, 2) == -5
    assert calc.divide(0, 1) == 0
    try:
        calc.divide(10, 0)
    except ValueError as e:
        assert str(e) == "Division by zero is not allowed."
