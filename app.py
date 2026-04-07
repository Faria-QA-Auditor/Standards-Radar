import streamlit as st
import pandas as pd

st.set_page_config(page_title="Standards Radar", page_icon="📡", layout="wide")

# Estilo personalizado para parecerse a una herramienta Premium
st.markdown("""
    <style>
    .main { background-color: #f5f7f9; }
    .stMetric { background-color: #ffffff; padding: 15px; border-radius: 10px; box-shadow: 0 2px 4px rgba(0,0,0,0.05); }
    </style>
    """, unsafe_allow_html=True)

st.title("📡 Standards Update Radar")
st.markdown("### Higher-level oversight for curriculum standards")

try:
    df = pd.read_csv("auditoria_beta_v1.csv")

    # --- SIDEBAR FILTERS (Como Visualping) ---
    st.sidebar.header("Filter Options")
    
    # Filtro por Organización
    search = st.sidebar.text_input("🔍 Search Organization")
    
    # Filtro por Estado
    status_filter = st.sidebar.multiselect(
        "Select Status", 
        options=df['Status'].unique(), 
        default=df['Status'].unique()
    )

    # Aplicar filtros
    filtered_df = df[df['Status'].isin(status_filter)]
    if search:
        filtered_df = filtered_df[filtered_df['Organization'].str.contains(search, case=False)]

    # --- METRICAS VISUALES ---
    c1, c2, c3 = st.columns(3)
    c1.metric("Total Sites", len(df))
    changes = len(df[df['Status'].str.contains("🚨")])
    c2.metric("Alerts Detected", changes, delta=changes, delta_color="inverse")
    c3.metric("Last Global Sync", df['Check Date'].iloc[0])

    st.divider()

    # --- TABLA INTERACTIVA ---
    st.subheader("Monitoring Log")
    
    # Configuración de columnas para que el link sea clickeable
    st.dataframe(
        filtered_df,
        column_config={
            "URL": st.column_config.LinkColumn("Direct Link"),
            "Hash": st.column_config.TextColumn("Digital Fingerprint", help="Unique ID of the page content"),
            "Status": st.column_config.TextColumn("Current Status")
        },
        use_container_width=True,
        hide_index=True
    )

    # --- ACCIONES EXTRA ---
    if st.button("📥 Export Report to CSV"):
        filtered_df.to_csv("filtered_standards_report.csv", index=False)
        st.success("Report ready for download!")

except Exception as e:
    st.error(f"Error loading data: {e}")
