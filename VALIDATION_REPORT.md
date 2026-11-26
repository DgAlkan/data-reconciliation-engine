# Validation report — v1.1

## Evidence — 2026-11-26

GitHub Actions workflow Tests #9 displayed a successful result [e79f11c](https://github.com/DgAlkan/data-reconciliation-engine/commit/e79f11c226a874123bc497bc1d8c4c56ac2a6e89). The workflow executes pytest, including Python, DuckDB integration and Streamlit AppTest checks. The earlier AppTest relative-path failure was corrected using an absolute path derived from the test file.

## Reproduce

```bash
pip install -r requirements.txt
python -m pytest -v
```

[Actions history](https://github.com/DgAlkan/data-reconciliation-engine/actions)
