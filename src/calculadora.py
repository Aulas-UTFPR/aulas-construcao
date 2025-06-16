class Calculadora:

    def soma(self, num1, num2):
        return num1 + num2

    def subtracao(self, num1, num2):
        return num1 - num2

    def multiplicacao(self, num1, num2):
        return num1 * num2

    def divisao(self, num1, num2):
        if num2 != 0:
            return num1 / num2
        else:
            return "Erro: divisão por zero"

def main():
    calc = Calculadora()
    print(calc.soma(2, 2))

if __name__ == "__main__":
    main()
