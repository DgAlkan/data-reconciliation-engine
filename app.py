import io
import pandas as pd
import streamlit as st
from engine import reconcile, export_excel

st.set_page_config(page_title="Data Reconciliation Engine", layout="wide")
st.caption("ANALYTICS INTELLIGENCE LAB / PORTFOLIO / V2.0")
st.title("Data Reconciliation Engine")
st.caption("Public demo: use synthetic data only. Never upload personal, confidential or employer data.")
mode = st.sidebar.selectbox("Demo dataset", ["Classic (4 records)", "Migration audit (5,000 records)"])
a = st.sidebar.file_uploader("Source CSV (synthetic only)", type="csv")
b = st.sidebar.file_uploader("Target CSV (synthetic only)", type="csv")
key = st.sidebar.text_input("Unique key", "id")
tol = st.sidebar.number_input("Absolute numeric tolerance", min_value=0.0, value=0.0)
rules = st.sidebar.text_input("Required nonnegative fields (comma separated)")
st.info("Compare records, inspect discrepancies and export audit evidence.")
if st.button("Run reconciliation", type="primary"):
    try:
        if bool(a) != bool(b):
            raise ValueError("Upload both files or neither")
        if a is None and mode.startswith("Migration"):
            source = pd.DataFrame({"id": [f"{i:06d}" for i in range(5000)], "category": ["ABC"[i%3] for i in range(5000)], "amount": [100+i%900 for i in range(5000)]})
            target = source.iloc[50:].copy()
            target.loc[target.index[::40], "amount"] += 5
            target.loc[target.index[::71], "category"] = "D"
            target = pd.concat([target, pd.DataFrame({"id":["009999"],"category":["C"],"amount":[-10]})], ignore_index=True)
        else:
            source = pd.read_csv(a or "data/source.csv", dtype={key: "string"})
            target = pd.read_csv(b or "data/target.csv", dtype={key: "string"})
        result = reconcile(source, target, key, tol, [x.strip() for x in rules.split(",") if x.strip()])
        m = result["summary"].iloc[0]
        for c, label, val in zip(st.columns(4), ["Source rows","Target rows","Key match rate","Different cells"], [f'{m.source_rows:,.0f}',f'{m.target_rows:,.0f}',"N/A" if pd.isna(m.key_match_rate) else f'{m.key_match_rate:.1%}',f'{m.different_cells:,.0f}']):
            c.metric(label,val)
        st.bar_chart(pd.Series({"Matched":m.matched_keys,"Source only":m.source_only,"Target only":m.target_only},name="Records"))
        tabs = st.tabs(["Overview","Field differences","Exclusive records","Quality checks"])
        for tab, names in zip(tabs,[["summary","schema"],["differences"],["source_only","target_only"],["nulls","rules"]]):
            with tab:
                for name in names:
                    st.subheader(name.replace("_"," ").title())
                    st.dataframe(result[name])
        buffer = io.BytesIO()
        export_excel(result, buffer)
        st.download_button("Download evidence", buffer.getvalue(), "evidence.xlsx")
    except (ValueError, TypeError, UnicodeError, OSError) as exc:
        st.error(str(exc))


st.divider()
st.caption("Rodrigo Alcantara | Analytics Intelligence Lab | Synthetic demonstration")
