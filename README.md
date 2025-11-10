# Exemplo Aula de Construção

## Criar o ambiente virtual:

```bash
python3 -m venv .venv
source .venv/bin/activate
pip3 install -r requirement.txt
```

## Notebooks

```
- teste_software.ipynb  Jupyter Notebook com exemplo de teste de software.
- tdd_python.ipynb      Jupyter Notebook com exemplo de TDD.
```

## Código

```
- linters/
 -  exemplo_limpo.py        Código para linters.
- calculadora.py            Código para testes.
```

## GitHub Actions

```
- .pre-commit-config.yaml   Config do pre-commit.
- .github/workflows/
 -  lint.yml                Action para linters.
 -  test.yml                Action para testes.
```

Para o pré-commit, use o seguinte commando:

```bash
pre-commit install
```

## GitHub Templates

```
- ./github/ISSUE_TEMPLATE/
 -  feature.md              Template para issue de nova feature.
 -  task.md                 Template para issue de nova tarefa.
 -  bug.md                  Template para issue de bug.
```