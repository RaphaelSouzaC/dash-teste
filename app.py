import streamlit as st
import pandas as pd
import plotly.express as px

# URL do CSV no GitHub (link raw)
CSV_URL = "https://raw.githubusercontent.com/RaphaelSouzaC/dash-teste/main/planilha_estoque.csv"

# Carregar dados
df = pd.read_csv(CSV_URL)

# Título
st.set_page_config(page_title="Dashboard de Estoque", layout="wide")
st.title("📊 Dashboard de Estoque")

# Filtros
col1, col2 = st.columns(2)
with col1:
    filtro_local = st.selectbox("Filtrar por Local", ["Todos"] + sorted(df['Local'].dropna().unique().tolist()))
with col2:
    filtro_status = st.selectbox("Filtrar por Status", ["Todos"] + sorted(df['Status'].dropna().unique().tolist()))

# Aplicar filtros
df_filtrado = df.copy()
if filtro_local != "Todos":
    df_filtrado = df_filtrado[df_filtrado['Local'] == filtro_local]
if filtro_status != "Todos":
    df_filtrado = df_filtrado[df_filtrado['Status'] == filtro_status]

# KPIs
total_itens = len(df_filtrado)
em_estoque = (df_filtrado['Status'] == "Estoque").sum()
em_uso = (df_filtrado['Status'] != "Estoque").sum()

st.markdown(f"**Total de Itens:** {total_itens}")
st.markdown(f"**Em Estoque:** {em_estoque}")
st.markdown(f"**Em Uso:** {em_uso}")

# Gráfico por Local
fig1 = px.bar(df_filtrado.groupby('Local').size().reset_index(name='Quantidade'),
              x='Local', y='Quantidade', title="Quantidade por Local")
st.plotly_chart(fig1, use_container_width=True)

# Gráfico por Status
fig2 = px.pie(df_filtrado, names='Status', title="Distribuição por Status")
st.plotly_chart(fig2, use_container_width=True)

# Mostrar tabela
st.subheader("📋 Dados Detalhados")
st.dataframe(df_filtrado)
