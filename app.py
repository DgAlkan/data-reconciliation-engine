import io
import pandas as pd
import streamlit as st
from engine import reconcile, export_excel

st.set_page_config(page_title="Data Reconciliation Engine", layout="wide")
lang = st.sidebar.radio("Idioma / Language", ["Português", "English"], horizontal=True, key="lab_language")
def tr(en, pt):
    return pt if lang == "Português" else en
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
<section class="lab-hero"><div class="lab-kicker">ANALYTICS INTELLIGENCE LAB</div><h1>Data Reconciliation Engine</h1><p>__LAB_SUBTITLE__</p></section>""".replace("__LAB_SUBTITLE__", tr("Data quality · Reconciliation · Audit evidence", "Qualidade de dados · Conciliação · Evidências de auditoria")), unsafe_allow_html=True)
st.sidebar.header(tr("Workspace", "Área de trabalho"))
st.sidebar.caption(tr("Configure your synthetic demonstration.", "Configure sua demonstração com dados sintéticos."))
st.sidebar.markdown(tr("### Product suite", "### Produtos"))
st.sidebar.markdown("[01 · Data Quality](https://dgalkan-data-quality.streamlit.app)  \n[02 · Decision Intelligence](https://dgalkan-decision-intelligence.streamlit.app)  \n[03 · Customer Journey](https://dgalkan-customer-journey.streamlit.app)")
st.sidebar.divider()
st.sidebar.markdown(tr("### Analysis controls", "### Filtros e parâmetros"))
with st.expander(tr("About this product · methodology", "Sobre o produto · metodologia")):
    st.markdown(tr("Audit migration quality and investigate discrepancies.", "Audite a qualidade da migração e investigue divergências."))
    st.markdown(tr("Unique-key alignment, null-aware field comparisons, numeric tolerance and configurable nonnegative rules. Key match rate measures coverage, not content accuracy.", "Cruzamento por chave única, comparação de campos e nulos, tolerância numérica e regras de valores não negativos. A taxa de correspondência mede cobertura, não exatidão do conteúdo."))
    st.markdown(tr("[Technical portfolio](https://github.com/DgAlkan) · Synthetic data only.", "[Portfólio técnico](https://github.com/DgAlkan) · Apenas dados sintéticos."))
st.caption(tr("Public demo: use synthetic data only. Never upload personal, confidential or employer data.", "Demonstração pública: use apenas dados sintéticos. Nunca envie dados pessoais, confidenciais ou do empregador."))
mode = st.sidebar.selectbox(tr("Demo dataset", "Base de demonstração"), ["Classic (4 records)", "Migration audit (5,000 records)"], format_func=lambda x: tr(x, {"Classic (4 records)":"Clássico (4 registros)", "Migration audit (5,000 records)":"Auditoria de migração (5.000 registros)"}[x]))
a = st.sidebar.file_uploader(tr("Source CSV (synthetic only)", "CSV de origem (apenas sintético)"), type="csv")
b = st.sidebar.file_uploader(tr("Target CSV (synthetic only)", "CSV de destino (apenas sintético)"), type="csv")
key = st.sidebar.text_input(tr("Unique key", "Chave única"), "id")
tol = st.sidebar.number_input(tr("Absolute numeric tolerance", "Tolerância numérica absoluta"), min_value=0.0, value=0.0)
rules = st.sidebar.text_input(tr("Required nonnegative fields (comma separated)", "Campos não negativos obrigatórios (separados por vírgula)"))
st.info(tr("Compare records, inspect discrepancies and export audit evidence.", "Compare registros, investigue divergências e exporte evidências."))
if st.button(tr("Run reconciliation", "Executar conciliação"), type="primary"):
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
        for c, label, val in zip(st.columns(4), [tr("Source rows", "Registros de origem"),tr("Target rows", "Registros de destino"),tr("Key match rate", "Taxa de correspondência"),tr("Different cells", "Divergências de conteúdo")], [f'{m.source_rows:,.0f}',f'{m.target_rows:,.0f}',"N/A" if pd.isna(m.key_match_rate) else f'{m.key_match_rate:.1%}',f'{m.different_cells:,.0f}']):
            c.metric(label,val)
        st.caption(tr(f"Matched {m.matched_keys:,} keys; investigate {m.different_cells:,} field differences and {m.source_only + m.target_only:,} exclusive records before migration approval.", f"{m.matched_keys:,} chaves correspondentes; investigue {m.different_cells:,} divergências de conteúdo e {m.source_only + m.target_only:,} registros exclusivos antes de aprovar a migração."))
        st.bar_chart(pd.Series({tr("Matched","Correspondentes"):m.matched_keys,tr("Source only","Só na origem"):m.source_only,tr("Target only","Só no destino"):m.target_only},name=tr("Records","Registros")))
        tabs = st.tabs([tr("Overview", "Visão geral"),tr("Field differences", "Divergências por campo"),tr("Exclusive records", "Registros exclusivos"),tr("Quality checks", "Verificações de qualidade")])
        for tab, names in zip(tabs,[["summary","schema"],["differences"],["source_only","target_only"],["nulls","rules"]]):
            with tab:
                for name in names:
                    st.subheader(tr(name.replace("_"," ").title(), {"summary":"Resumo","schema":"Estrutura","differences":"Divergências","source_only":"Exclusivos da origem","target_only":"Exclusivos do destino","nulls":"Valores nulos","rules":"Regras"}[name]))
                    st.dataframe(result[name])
        buffer = io.BytesIO()
        export_excel(result, buffer)
        st.download_button(tr("Download evidence", "Baixar evidências"), buffer.getvalue(), "evidence.xlsx")
    except (ValueError, TypeError, UnicodeError, OSError) as exc:
        st.error(str(exc))


st.divider()
st.caption(tr("Rodrigo Alcantara | Analytics Intelligence Lab | Independent synthetic demonstration", "Rodrigo Alcantara | Analytics Intelligence Lab | Demonstração independente com dados sintéticos"))
st.markdown("[Data Quality](https://dgalkan-data-quality.streamlit.app) · [Decision Intelligence](https://dgalkan-decision-intelligence.streamlit.app) · [Customer Journey](https://dgalkan-customer-journey.streamlit.app)")
