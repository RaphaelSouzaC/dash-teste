import streamlit as st
import pandas as pd

st.set_page_config(page_title="Dashboard de Estoque", layout="wide")

# ===== Carregar dados =====
# Substitua pelo caminho do seu arquivo no GitHub ou local
url_arquivo = "planilha_estoque.csv"  # Ou caminho/URL correto
df = pd.read_csv(url_arquivo)

# Limpar nomes de colunas
df.columns = df.columns.str.strip()

# Mostrar colunas carregadas (debug)
st.write("Colunas encontradas:", df.columns.tolist())

# ===== Detectar coluna 'Local' =====

# ===== Filtro por Local =====
opcoes_locais = ["Todos"] + sorted(df[coluna_local].dropna().unique().tolist())
filtro_local = st.selectbox("Filtrar por Local", opcoes_locais)

if filtro_local != "Todos":
    df = df[df[coluna_local] == filtro_local]

# ===== Mostrar tabela filtrada =====
st.dataframe(df)

# ===== Estatísticas =====
st.metric("Total de Itens", len(df))
if "Quantidade" in df.columns:
    st.metric("Quantidade Total em Estoque", df["Quantidade"].sum())

