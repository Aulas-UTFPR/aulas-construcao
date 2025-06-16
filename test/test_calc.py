import sys
import os
import pytest

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'src')))

from calculadora import Calculadora

def test_soma_1():
    calc = Calculadora()
    assert calc.soma(2,2) == 4

def test_soma():
    calc = Calculadora()
    assert calc.soma(2,3) == 5

def test_sub():
    calc = Calculadora()
    assert calc.subtracao(2,2) == 0

def test_div():
    calc = Calculadora()
    assert calc.divisao(2,1) == 2