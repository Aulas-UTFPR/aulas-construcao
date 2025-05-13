# Exemplo Aula de Construção

*Criar o ambiente virtual:*

```bash
python3 -m venv .venv
source .venv/bin/activate
pip3 install -r requirement.txt
```

*Criar o pre-commit hook (opcional):*

```bash
pre-commit install
```

*Executar flake8:*

```bash
flake8 .
```