
import streamlit as st
import pandas as pd
import numpy as np
from io import BytesIO

st.set_page_config(page_title="COFCO INTL • Inventory Dashboard", page_icon="📊", layout="wide")

# ---- THEME (Power BI inspired) ----
# Subtle CSS to mimic Power BI cards and spacing
st.markdown("""
    <style>
        .cofco-header {display:flex; align-items:center; gap:16px; margin-bottom:0.8rem;}
        .cofco-title {font-weight:700; font-size:1.6rem; line-height:1; margin:0;}
        .subtle {color:#6b7280;}
        .kpi-card {
            border-radius:16px; padding:16px; 
            background: #ffffff;
            border: 1px solid #e5e7eb;
            box-shadow: 0 1px 2px rgba(0,0,0,0.04);
        }
        .kpi-label {font-size:0.85rem; color:#6b7280; margin-bottom:6px;}
        .kpi-value {font-size:1.7rem; font-weight:700; line-height:1.2;}
        .kpi-foot {font-size:0.8rem; color:#9ca3af;}
        .card {
            border-radius:16px; padding:16px; background:#ffffff; 
            border:1px solid #e5e7eb; box-shadow:0 1px 2px rgba(0,0,0,0.04);
        }
        .stTabs [data-baseweb="tab-list"] { gap: 8px; }
        .stTabs [data-baseweb="tab"] {
            height: 38px; background: #f3f4f6; border-radius: 999px; padding: 6px 14px;
        }
        .stTabs [aria-selected="true"] {
            background: #111827 !important; color: #ffffff !important;
        }
    </style>
""", unsafe_allow_html=True)

# ---- Logo (online) ----
LOGO_URLS = [
    "https://www.cofcointernational.com/themes/custom/cofco/logo.svg",
    "https://upload.wikimedia.org/wikipedia/commons/0/0b/COFCO_logo.svg"
]

def render_header():
    logo_loaded = False
    cols = st.columns([1, 8])
    with cols[0]:
        for url in LOGO_URLS:
            try:
                st.image(url, use_column_width=True)
                logo_loaded = True
                break
            except Exception:
                continue
    with cols[1]:
        st.markdown('<div class="cofco-header"><h1 class="cofco-title">Inventory Dashboard</h1></div>', unsafe_allow_html=True)
        st.markdown('<div class="subtle">Power BI–style Streamlit app • COFCO International</div>', unsafe_allow_html=True)

render_header()
st.markdown("---")

# ---- Data Loader ----
@st.cache_data(show_spinner=True)
def load_excel(path_or_buffer):
    xls = pd.ExcelFile(path_or_buffer)
    sheets = {}
    for sh in xls.sheet_names:
        try:
            df0 = pd.read_excel(path_or_buffer, sheet_name=sh, header=None)
            # Heuristic: find header row by looking for a row that contains many non-null values
            header_row = None
            for i in range(min(10, len(df0))):
                non_nulls = df0.iloc[i].notna().sum()
                if non_nulls >= 4:
                    header_row = i
                    break
            if header_row is None:
                header_row = 0
            df = pd.read_excel(path_or_buffer, sheet_name=sh, header=header_row)
            # Drop completely empty columns
            df = df.loc[:, ~df.columns.astype(str).str.startswith("Unnamed")]
            sheets[sh] = df
        except Exception as e:
            sheets[sh] = pd.DataFrame({"_error": [str(e)]})
    return sheets

# ---- Sidebar Upload / Sheet selection ----
with st.sidebar:
    st.subheader("Data")
    uploaded = st.file_uploader("Upload your inventory Excel", type=["xlsx", "xls"])
    if uploaded:
        sheets = load_excel(uploaded)
    else:
        # Fallback to example baked into the repo (if present)
        try:
            sheets = load_excel("Planilha de estoque viva PORTS & SOFTS.xlsx")
        except Exception:
            sheets = {}

    if not sheets:
        st.info("Upload an Excel file (.xlsx) with your inventory data.")
        st.stop()

    sheet_names = list(sheets.keys())
    # Prefer TEC if present
    default_idx = sheet_names.index("TEC") if "TEC" in sheet_names else 0
    sheet = st.selectbox("Sheet", sheet_names, index=default_idx)

df = sheets.get(sheet, pd.DataFrame())
if df.empty:
    st.warning("Selected sheet is empty or could not be parsed.")
    st.stop()

# Standardize column names
df.columns = [str(c).strip() for c in df.columns]

# Try to identify common columns
def pick_col(df, candidates):
    for c in df.columns:
        norm = c.lower()
        for cand in candidates:
            if cand in norm:
                return c
    return None

col_item = pick_col(df, ["ativo", "item", "produto", "consumiveis", "ativos", "descri", "equipamento"])
col_status = pick_col(df, ["status", "situa", "situacao"])
col_brand = pick_col(df, ["marca", "brand"])
col_model = pick_col(df, ["modelo", "model"])
col_user = pick_col(df, ["usuario", "user"])
col_location = pick_col(df, ["setor", "centro de custo", "aloc", "local"])
col_date = pick_col(df, ["data", "entrega", "atualiza", "compra"])

# ---- Sidebar Filters ----
with st.sidebar:
    st.subheader("Filters")
    if col_status and df[col_status].notna().any():
        status_vals = sorted([str(x) for x in df[col_status].dropna().unique()])
        f_status = st.multiselect("Status", status_vals, default=status_vals)
    else:
        f_status = None

    if col_brand and df[col_brand].notna().any():
        brand_vals = sorted([str(x) for x in df[col_brand].dropna().unique()])
        f_brand = st.multiselect("Brand", brand_vals)
    else:
        f_brand = None

    if col_location and df[col_location].notna().any():
        loc_vals = sorted([str(x) for x in df[col_location].dropna().unique()])
        f_loc = st.multiselect("Location/Cost Center", loc_vals)
    else:
        f_loc = None

    if col_model and df[col_model].notna().any():
        model_vals = sorted([str(x) for x in df[col_model].dropna().unique()])
        f_model = st.multiselect("Model", model_vals)
    else:
        f_model = None

    search_text = st.text_input("Search (any column)").strip()

# Apply filters
df_f = df.copy()
if f_status is not None:
    df_f = df_f[df_f[col_status].astype(str).isin(f_status)]
if f_brand:
    df_f = df_f[df_f[col_brand].astype(str).isin(f_brand)]
if f_loc:
    df_f = df_f[df_f[col_location].astype(str).isin(f_loc)]
if f_model:
    df_f = df_f[df_f[col_model].astype(str).isin(f_model)]
if search_text:
    mask = pd.Series(False, index=df_f.index)
    for c in df_f.columns:
        mask |= df_f[c].astype(str).str.contains(search_text, case=False, na=False)
    df_f = df_f[mask]

# ---- KPIs ----
total_items = int(len(df_f))
in_use = None
in_stock = None
reserved = None
unknown = None

if col_status:
    s = df_f[col_status].astype(str).str.upper().str.strip()
    in_use = int((s == "EM USO").sum())
    in_stock = int((s == "EM ESTOQUE").sum())
    reserved = int((s == "RESERVADO").sum())
    unknown = int((s.isna() | (s == "NAN")).sum()) if df_f[col_status].isna().any() else int((~s.isin(["EM USO","EM ESTOQUE","RESERVADO"])).sum())

k1, k2, k3, k4 = st.columns(4)
with k1:
    st.markdown('<div class="kpi-card"><div class="kpi-label">Total items</div><div class="kpi-value">{:,}</div></div>'.format(total_items), unsafe_allow_html=True)
with k2:
    val = in_use if in_use is not None else "-"
    st.markdown('<div class="kpi-card"><div class="kpi-label">In use</div><div class="kpi-value">{}</div></div>'.format(val), unsafe_allow_html=True)
with k3:
    val = in_stock if in_stock is not None else "-"
    st.markdown('<div class="kpi-card"><div class="kpi-label">In stock</div><div class="kpi-value">{}</div></div>'.format(val), unsafe_allow_html=True)
with k4:
    val = reserved if reserved is not None else "-"
    st.markdown('<div class="kpi-card"><div class="kpi-label">Reserved / Other</div><div class="kpi-value">{}</div></div>'.format(val), unsafe_allow_html=True)

st.markdown("")

# ---- Charts ----
t1, t2 = st.tabs(["📊 Charts", "📋 Table"])

with t1:
    c1, c2 = st.columns(2)
    with c1:
        st.markdown('<div class="card">', unsafe_allow_html=True)
        st.subheader("Items by Category")
        cat_col = col_item if col_item else (df_f.columns[0] if len(df_f.columns) else None)
        if cat_col:
            top_counts = df_f[cat_col].astype(str).value_counts().head(15).sort_values(ascending=True)
            st.bar_chart(top_counts)
        else:
            st.info("No category column detected.")
        st.markdown('</div>', unsafe_allow_html=True)

    with c2:
        st.markdown('<div class="card">', unsafe_allow_html=True)
        st.subheader("Items by Delivery Date (Monthly)")
        if col_date:
            dfx = df_f.copy()
            dfx[col_date] = pd.to_datetime(dfx[col_date], errors="coerce")
            dfx = dfx.dropna(subset=[col_date])
            if not dfx.empty:
                dfx["_month"] = dfx[col_date].dt.to_period("M").dt.to_timestamp()
                series = dfx.groupby("_month").size().sort_index()
                st.line_chart(series)
            else:
                st.info("No valid dates found to plot.")
        else:
            st.info("No date column detected.")
        st.markdown('</div>', unsafe_allow_html=True)

# ---- Table ----
with t2:
    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.dataframe(df_f, use_container_width=True, hide_index=True)
    st.markdown('</div>', unsafe_allow_html=True)

# ---- Download filtered data ----
def to_excel_bytes(df):
    out = BytesIO()
    with pd.ExcelWriter(out, engine="xlsxwriter") as writer:
        df.to_excel(writer, index=False, sheet_name="Filtered")
    return out.getvalue()

st.download_button("Download filtered data (Excel)", data=to_excel_bytes(df_f), file_name="inventory_filtered.xlsx", mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")
