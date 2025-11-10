"""Módulo de exemplo para validação com flake8, mypy, pylint e vulture."""


def somar(a: int, b: int) -> int:
    """Retorna a soma de dois inteiros.."""
    return a + b


def classificar_pontuacao(pontos: int) -> str:
    """Classifica o nível de um jogador com base na pontuação."""
    if pontos < 0:
        return "Pontuação inválida"
    if pontos == 0:
        return "Iniciante"
    if pontos <= 50:
        return "Intermediário"
    return "Avançado"


def main() -> None:
    """Função principal de execução."""
    resultado: int = somar(10, 5)
    print(f"Resultado da soma: {resultado}")

    classificacao: str = classificar_pontuacao(resultado)
    print(f"Classificação: {classificacao}")


if __name__ == "__main__":
    main()
