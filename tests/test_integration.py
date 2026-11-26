from pathlib import Path
import pandas as pd
import duckdb
from openpyxl import load_workbook
from streamlit.testing.v1 import AppTest
from engine import reconcile, export_excel

def test_boolean():
    a=pd.DataFrame({"id":[1],"flag":[True]})
    b=pd.DataFrame({"id":[1],"flag":[False]})
    assert len(reconcile(a,b)["differences"])==1

def test_sql_and_excel(tmp_path):
    a=pd.read_csv("data/source.csv")
    b=pd.read_csv("data/target.csv")
    r=reconcile(a,b)
    with duckdb.connect() as con:
        sql=con.execute(open("sql/reconciliation.sql").read()).df()
    assert (sql.status=="source_only").sum()==r["summary"].iloc[0].source_only
    assert (sql.status=="target_only").sum()==r["summary"].iloc[0].target_only
    p=tmp_path/"evidence.xlsx"
    export_excel(r,p)
    w=load_workbook(p)
    assert set(w.sheetnames)==set(r)
    assert w["differences"].max_row==len(r["differences"])+1

def test_app():
    a=AppTest.from_file(str(Path(__file__).resolve().parents[1] / "app.py")).run()
    assert not a.exception
    a.button[0].click().run()
    assert not a.exception
    assert len(a.dataframe)>=7
