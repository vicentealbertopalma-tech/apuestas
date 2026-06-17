import streamlit as st

st.set_page_config(page_title="Análisis Profundo", layout="wide")

st.title("📊 Análisis Estadístico Detallado")
st.write("Aquí puedes ver el desglose de córners, tarjetas y tiros al arco.")

# Selector de partido para análisis
partido = st.selectbox("Selecciona un partido para analizar:", ["Argentina vs Algeria", "Brasil vs Inglaterra"])

# Aquí puedes poner la lógica de los expanders que funcionaban bien
with st.expander("Desglose de Córners"):
    st.write("Estadísticas históricas de córners...")
    
with st.expander("Desglose de Tarjetas"):
    st.write("Estadísticas disciplinarias...")
