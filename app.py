import streamlit as st
import pandas as pd
import plotly.express as px

# ---------------------
# CONFIGURAÇÃO INICIAL
# ---------------------
st.set_page_config(page_title="Dashboard de Estoque", layout="wide")

# URL do CSV no GitHub (troque pela sua)
url_csv = "https://raw.githubusercontent.com/seu_usuario/seu_repositorio/main/planilha_estoque.csv"

# Ler dados
df = pd.read_csv(url_csv)

# ---------------------
# LIMPEZA DE DADOS
# ---------------------
df.columns = [col.strip() for col in df.columns]  # remove espaços extras
if "Status" not in df.columns:
    st.error("A coluna 'Status' não foi encontrada no CSV.")
    st.stop()

# ---------------------
# KPIs
# ---------------------
total_itens = len(df)
total_estoque = df[df["Status"].str.contains("Estoque", case=False, na=False)].shape[0]
total_uso = df[df["Status"].str.contains("Em uso", case=False, na=False)].shape[0]

col1, col2, col3 = st.columns(3)
col1.metric("Total de Itens", total_itens)
col2.metric("Em Estoque", total_estoque)
col3.metric("Em Uso", total_uso)

# ---------------------
# FILTROS
# ---------------------
col_filtro1, col_filtro2 = st.columns(2)
status_selecionado = col_filtro1.multiselect("Filtrar por Status:", df["Status"].dropna().unique())
categoria_selecionada = col_filtro2.multiselect("Filtrar por Categoria:", df["Categoria"].dropna().unique() if "Categoria" in df.columns else [])

df_filtrado = df.copy()
if status_selecionado:
    df_filtrado = df_filtrado[df_filtrado["Status"].isin(status_selecionado)]
if categoria_selecionada and "Categoria" in df.columns:
    df_filtrado = df_filtrado[df_filtrado["Categoria"].isin(categoria_selecionada)]

# ---------------------
# GRÁFICOS
# ---------------------
st.subheader("Distribuição por Status")
fig_status = px.histogram(df_filtrado, x="Status", color="Status", title="Quantidade por Status")
st.plotly_chart(fig_status, use_container_width=True)

if "Categoria" in df.columns:
    st.subheader("Distribuição por Categoria")
    fig_cat = px.histogram(df_filtrado, x="Categoria", color="Categoria", title="Quantidade por Categoria")
    st.plotly_chart(fig_cat, use_container_width=True)

# ---------------------
# TABELA
# ---------------------
st.subheader("Tabela de Estoque")
st.dataframe(df_filtrado)

