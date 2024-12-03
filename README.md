# Simple Codes

*Create a virtual environment:*

```bash
python3 -m venv .venv
source .venv/bin/activate
pip3 install pytest pytest-html pytest-cov
```

*Remove any trash:*
```bash
find . -name "__pycache__" -exec rm -rf {} +
```

## Calculator

Simple code example used for unit testing in `calculator` folder.

```bash
pip3 install -e .
pytest
pytest --cov=calculator --cov-report=html
```
