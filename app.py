import streamlit as st
import pandas as pd
import plotly.express as px

# =========================
# CONFIGURAÇÃO DO APP
# =========================
st.set_page_config(page_title="Dashboard de Estoque", layout="wide")

st.title("📦 Dashboard de Estoque")
st.markdown("Visualize e analise o estoque de forma rápida e interativa.")

# =========================
# IMPORTAÇÃO E AJUSTES DE DADOS
# =========================
df = pd.read_excel("estoque.xlsx")
df.columns = df.columns.str.strip()

# Garantir coluna 'Local'
if 'Local' not in df.columns:
    if 'CENTRO DE CUSTO' in df.columns:
        df['Local'] = df['CENTRO DE CUSTO']
    else:
        df['Local'] = "Não informado"

# Garantir coluna 'Categoria'
if 'Categoria' not in df.columns:
    df['Categoria'] = "Não informado"

# Garantir coluna 'Produto'
if 'Produto' not in df.columns:
    df['Produto'] = df.iloc[:, 0]  # usa a primeira coluna como nome do produto

# =========================
# FILTROS LATERAIS
# =========================
st.sidebar.header("Filtros")

locais = st.sidebar.multiselect("📍 Selecione Local", options=df['Local'].unique(), default=df['Local'].unique())
categorias = st.sidebar.multiselect("🏷️ Selecione Categoria", options=df['Categoria'].unique(), default=df['Categoria'].unique())
produtos = st.sidebar.multiselect("📦 Selecione Produto", options=df['Produto'].unique(), default=df['Produto'].unique())

# Aplicar filtros
df_filtrado = df[
    (df['Local'].isin(locais)) &
    (df['Categoria'].isin(categorias)) &
    (df['Produto'].isin(produtos))
]

# =========================
# MÉTRICAS PRINCIPAIS
# =========================
col1, col2, col3 = st.columns(3)
col1.metric("Total de Itens", len(df_filtrado))
col2.metric("Locais Diferentes", df_filtrado['Local'].nunique())
col3.metric("Categorias Diferentes", df_filtrado['Categoria'].nunique())

# =========================
# GRÁFICOS
# =========================
st.subheader("📊 Estoque por Local")
fig1 = px.histogram(df_filtrado, x="Local", title="Quantidade por Local", text_auto=True)
st.plotly_chart(fig1, use_container_width=True)

st.subheader("📊 Estoque por Categoria")
fig2 = px.histogram(df_filtrado, x="Categoria", title="Quantidade por Categoria", text_auto=True)
st.plotly_chart(fig2, use_container_width=True)

# =========================
# TABELA FINAL
# =========================
st.subheader("📋 Tabela de Estoque")
st.dataframe(df_filtrado, use_container_width=True)
