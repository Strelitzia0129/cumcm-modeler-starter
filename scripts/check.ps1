$ErrorActionPreference = "Stop"

python -m pip install -e ".[dev]"
python -m unittest discover -s tests -v
python scripts/verify_repository.py
ruff check src tests scripts examples

