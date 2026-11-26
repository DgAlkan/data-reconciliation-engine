import io
import pandas as pd
import streamlit as st
from engine import reconcile, export_excel

st.set_page_config(page_title="Data Reconciliation Engine", layout="wide")
st.markdown("""<style>
.stApp {background:#f1f5f9;}
[data-testid="stSidebar"] {background:#142238;}
[data-testid="stSidebar"] [data-testid="stWidgetLabel"] p,
[data-testid="stSidebar"] [data-testid="stMarkdownContainer"] p,
[data-testid="stSidebar"] h2 {color:#e2e8f0;}
[data-testid="stMetric"] {background:white;border:1px solid #dbe4ef;border-radius:14px;padding:16px;box-shadow:0 3px 12px #10223808;}
[data-testid="stMetricValue"] {font-weight:700;color:#102238;}
[data-testid="stMainBlockContainer"] {padding-top:2rem;max-width:1440px;}
.stTabs [role="tablist"] {gap:12px;}
.stTabs [role="tab"] {font-weight:600;}
.lab-hero {background:linear-gradient(115deg,#0b1526,#193a60);color:white;padding:28px 30px;border-radius:16px;margin-bottom:18px;}
.lab-hero h1 {color:white;font-size:clamp(1.65rem,3vw,2.5rem);margin:8px 0;padding:0;}
.lab-hero p {color:#cbd5e1;margin:0;}
.lab-kicker {color:#7dd3fc;font-size:12px;font-weight:700;letter-spacing:1.8px;}
</style>
<section class="lab-hero"><div class="lab-kicker">ANALYTICS INTELLIGENCE LAB / 01 / V2.2</div><h1>Data Reconciliation Engine</h1><p>Data quality · Reconciliation · Audit evidence</p></section>""", unsafe_allow_html=True)
st.sidebar.header("Workspace")
st.sidebar.caption("Configure your synthetic demonstration.")
st.sidebar.markdown("### Product suite")
st.sidebar.markdown("[01 · Data Quality](https://dgalkan-data-quality.streamlit.app)  \n[02 · Decision Intelligence](https://dgalkan-decision-intelligence.streamlit.app)  \n[03 · Customer Journey](https://dgalkan-customer-journey.streamlit.app)")
st.sidebar.divider()
st.sidebar.markdown("### Analysis controls")
with st.expander("About this product · methodology"):
    st.markdown("Audit migration quality and investigate discrepancies.")
    st.markdown("Unique-key alignment, null-aware field comparisons, numeric tolerance and configurable nonnegative rules. Key match rate measures coverage, not content accuracy.")
    st.markdown("[Technical portfolio](https://github.com/DgAlkan) · Synthetic data only.")
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
        st.caption(f"Matched {m.matched_keys:,} keys; investigate {m.different_cells:,} field differences and {m.source_only + m.target_only:,} exclusive records before migration approval.")
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
st.caption("Rodrigo Alcantara | Analytics Intelligence Lab | Independent synthetic demonstration")
st.markdown("[Data Quality](https://dgalkan-data-quality.streamlit.app) · [Decision Intelligence](https://dgalkan-decision-intelligence.streamlit.app) · [Customer Journey](https://dgalkan-customer-journey.streamlit.app)")
