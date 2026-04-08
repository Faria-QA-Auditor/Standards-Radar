import streamlit as st
import pandas as pd
from datetime import datetime

st.set_page_config(page_title="Standards Radar", page_icon="📡", layout="wide")

# --- LOGO LOCAL ---
# Asegúrate de que "logo.png" sea el nombre exacto de tu archivo en GitHub
try:
    st.sidebar.image("logo.jpg", use_container_width=True)
except:
    st.sidebar.warning("Logo file 'logo.jpg' not found in repository.")

st.sidebar.divider()

st.title("📡 Standards Update Radar")
st.markdown("🔍 *Global oversight for Faria Education Group*")

try:
    df = pd.read_csv("auditoria_beta_v1.csv")

    # Filtros
    st.sidebar.header("Filter & Search")
    search = st.sidebar.text_input("🔍 Search Organization")
    status_filter = st.sidebar.multiselect("Status", options=df['Status'].unique(), default=df['Status'].unique())

    filtered_df = df[df['Status'].isin(status_filter)]
    if search:
        filtered_df = filtered_df[filtered_df['Organization'].str.contains(search, case=False)]

    # Tabla sin el Fingerprint
    st.dataframe(
        filtered_df,
        column_config={
            "Organization": "State / Organization",
            "Subject": "Subject Area",
            "Status": "Live Status",
            "Check Date": "Last Verified",
            "Mapped Version": "Current Faria Version",
            "URL": st.column_config.LinkColumn("Source Link"),
            "Hash": None # Sigue oculto aquí
        },
        use_container_width=True,
        hide_index=True
    )

except Exception as e:
    st.info("The system is currently updating the data. Please run the GitHub Action.")
