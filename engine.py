"""Independent, in-memory reconciliation engine. No corporate data."""
import pandas as pd

def reconcile(source, target, key="id", tolerance=0.0, nonnegative=()):
    if tolerance < 0:
        raise ValueError("Tolerance must be nonnegative")
    for frame in (source, target):
        if key not in frame or frame[key].isna().any() or frame[key].duplicated().any():
            raise ValueError("Each input requires a unique, non-null key")
    a, b = source.set_index(key), target.set_index(key)
    common = a.index.intersection(b.index)
    columns = a.columns.intersection(b.columns)
    schema = pd.DataFrame([{"field": c, "source_type": str(a[c].dtype) if c in a else "missing",
                            "target_type": str(b[c].dtype) if c in b else "missing"}
                           for c in a.columns.union(b.columns)])
    differences = []
    for c in columns:
        x, y = a.loc[common, c], b.loc[common, c]
        equal = (x.eq(y).fillna(False) | (x.isna() & y.isna()))
        if pd.api.types.is_numeric_dtype(x) and pd.api.types.is_numeric_dtype(y) and not pd.api.types.is_bool_dtype(x) and not pd.api.types.is_bool_dtype(y):
            equal = equal | ((x-y).abs() <= tolerance).fillna(False)
        for k in common[~equal]:
            differences.append({"key": k, "field": c, "source": x.loc[k], "target": y.loc[k]})
    diff = pd.DataFrame(differences, columns=["key","field","source","target"])
    rules = []
    for side, frame in (("source", a), ("target", b)):
        for c in nonnegative:
            if c not in frame:
                raise ValueError(f"Rule field missing: {c}")
            for k in frame.index[frame[c].isna() | (pd.to_numeric(frame[c], errors="coerce").isna()) | (pd.to_numeric(frame[c], errors="coerce") < 0)]:
                rules.append({"side": side, "key": k, "field": c, "rule": "nonnegative_required"})
    return {
        "summary": pd.DataFrame([{"source_rows": len(a), "target_rows": len(b),
            "matched_keys": len(common), "source_only": len(a.index.difference(b.index)),
            "target_only": len(b.index.difference(a.index)), "different_cells": len(diff),
            "key_match_rate": len(common)/len(a) if len(a) else None}]),
        "schema": schema, "differences": diff,
        "source_only": a.loc[a.index.difference(b.index)].reset_index(),
        "target_only": b.loc[b.index.difference(a.index)].reset_index(),
        "nulls": pd.concat([a.isna().sum().rename("source"), b.isna().sum().rename("target")], axis=1).reset_index(),
        "rules": pd.DataFrame(rules, columns=["side","key","field","rule"])
    }

def export_excel(results, destination):
    with pd.ExcelWriter(destination, engine="openpyxl", engine_kwargs={}) as writer:
        for name, frame in results.items():
            safe = frame.copy()
            for c in safe.columns:
                safe[c] = safe[c].map(lambda v: "'" + v if isinstance(v, str) and v.startswith(("=", "+", "-", "@", "\t", "\r")) else v)
            safe.to_excel(writer, sheet_name=name, index=False)
