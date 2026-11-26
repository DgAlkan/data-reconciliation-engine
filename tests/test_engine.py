import pandas as pd
import pytest
from engine import reconcile, export_excel

def test_demo(tmp_path):
    result = reconcile(pd.read_csv("data/source.csv"), pd.read_csv("data/target.csv"), nonnegative=["amount"])
    s = result["summary"].iloc[0]
    assert s.matched_keys == 3
    assert s.key_match_rate == .75
    assert s.source_only == s.target_only == 1
    assert s.different_cells == 2
    assert len(result["rules"]) == 1
    export_excel(result, tmp_path / "report.xlsx")
    assert (tmp_path / "report.xlsx").exists()

@pytest.mark.parametrize("ids", [[1,1],[1,None]])
def test_invalid_key(ids):
    with pytest.raises(ValueError):
        reconcile(pd.DataFrame({"id":ids}), pd.DataFrame({"id":[1]}))

def test_null_and_tolerance():
    a = pd.DataFrame({"id":[1,2], "value":[None,1.0]})
    b = pd.DataFrame({"id":[1,2], "value":[None,1.01]})
    assert reconcile(a,b,tolerance=.02)["differences"].empty
    assert len(reconcile(a,b)["differences"]) == 1

def test_schema():
    a = pd.DataFrame({"id":[1], "a":[1]})
    b = pd.DataFrame({"id":[1], "b":[1]})
    assert "missing" in reconcile(a,b)["schema"].target_type.values
