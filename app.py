import streamlit as st
import pandas as pd

st.set_page_config(page_title="Standards Radar", layout="wide")

st.title("📡 Standards Update Radar")

try:
    # Intentamos leer el archivo
    df = pd.read_csv("auditoria_beta_v1.csv")
    
    if df.empty or len(df.columns) < 2:
        st.warning("The database is currently empty. Please run the tracker in GitHub Actions.")
    else:
        # Métricas
        c1, c2 = st.columns(2)
        c1.metric("Total Sites", len(df))
        
        # Mostrar tabla
        st.subheader("Current Status")
        st.dataframe(df, use_container_width=True, hide_index=True)

except Exception as e:
    st.error(f"Waiting for initial data... (Error: {e})")
    st.info("Please go to GitHub Actions and run the 'Standards Radar Update' workflow.")
