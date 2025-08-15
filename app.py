import streamlit as st
import pandas as pd

# Carregar dados
df = pd.read_excel("estoque.xlsx")

# Normalizar nomes de colunas (remove espaços extras e coloca maiúsculas padronizadas)
df.columns = df.columns.str.strip()

# Garantir que a coluna 'Local' exista
if 'Local' not in df.columns:
    if 'CENTRO DE CUSTO' in df.columns:
        df['Local'] = df['CENTRO DE CUSTO']  # Usa Centro de Custo como Local
    else:
        df['Local'] = "Não informado"  # Se nem Centro de Custo existir, cria com valor padrão

# Filtro por Local
filtro_local = st.selectbox(
    "Filtrar por Local",
    ["Todos"] + sorted(df['Local'].dropna().unique().tolist())
)

# Aplicar filtro
if filtro_local != "Todos":
    df = df[df['Local'] == filtro_local]

# Mostrar tabela
st.dataframe(df)

# Mostrar métricas rápidas
st.metric("Total de Registros", len(df))
st.metric("Colunas no Dataset", len(df.columns))
