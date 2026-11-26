import io
import pandas as pd
import streamlit as st
from engine import reconcile, export_excel

st.set_page_config(page_title="Data Reconciliation Engine", layout="wide")
st.title("Data Reconciliation Engine")
st.caption("Use synthetic or authorized non-sensitive data only.")
a = st.file_uploader("Source CSV", type="csv")
b = st.file_uploader("Target CSV", type="csv")
key = st.text_input("Unique key", "id")
tol = st.number_input("Absolute numeric tolerance", min_value=0.0, value=0.0)
rules = st.text_input("Required nonnegative fields (comma separated)")
if st.button("Run reconciliation"):
    try:
        if bool(a) != bool(b):
            raise ValueError("Upload both files or neither")
        result = reconcile(pd.read_csv(a or "data/source.csv"), pd.read_csv(b or "data/target.csv"), key, tol, [x.strip() for x in rules.split(",") if x.strip()])
        for name, frame in result.items():
            st.subheader(name.replace("_"," ").title())
            st.dataframe(frame)
        buffer = io.BytesIO()
        export_excel(result, buffer)
        st.download_button("Download evidence", buffer.getvalue(), "evidence.xlsx")
    except (ValueError, TypeError) as exc:
        st.error(str(exc))
