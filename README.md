# Data Reconciliation Engine

Version 1.0 | Independent portfolio project | Rodrigo Alcantara (DgAlkan), developed with AI assistance.

A reproducible Python framework for comparing datasets after migration or transformation. Includes schema profiling, unique-key validation, key coverage, field-level differences, null counts, nonnegative business rules and Excel evidence.

## Quick start

```bash
python -m venv .venv
# Activate the environment for your operating system
pip install -r requirements.txt
python -m pytest -q
streamlit run app.py
```

Run without uploads to use synthetic CSVs. Enter amount in the business-rule field to demonstrate validation.

## Expected synthetic results

| Metric | Expected |
|---|---:|
| Source / target rows | 4 / 4 |
| Matched keys | 3 |
| Source key coverage | 75% |
| Exclusive keys (each side) | 1 |
| Different cells | 2 |
| Nonnegative violations | 1 |

Fixture expectations, not corporate performance claims. Key coverage is not cell accuracy.

## Repository structure

- engine.py: reconciliation and Excel export
- app.py: Streamlit interface
- data/: synthetic fixtures
- tests/: automated tests
- sql/: DuckDB full outer join example (requires DuckDB separately)
- [Architecture and limitations](docs/architecture.md)

## Limitations

Single unique key, in-memory CSV processing, inferred types, absolute numeric tolerance. No production-scale benchmark, authentication or hosted deployment. Use only synthetic or authorized non-sensitive data. Review outputs before sharing. No employer data, code or credentials are included.

## Original repository introduction

# data-reconciliation-engine
A Python and SQL framework for automated data reconciliation, quality assessment and business rules validation.

