import streamlit as st
import pandas as pd
import random

st.set_page_config(page_title="BetAnalytics Pro", layout="wide")

# CSS para que se vea idéntico a una casa de apuestas
st.markdown("""
<style>
    .top-bar { background-color: #ff5200; color: white; padding: 20px; font-weight: 900; font-size: 24px; border-radius: 0 0 10px 10px; margin-bottom: 20px; text-align: center;}
    .match-card { background: #1a1a1a; padding: 15px; border-radius: 8px; border-left: 4px solid #ff5200; margin-bottom: 10px; color: white;}
</style>
""", unsafe_allow_html=True)

st.markdown('<div class="top-bar">BETANALYTICS PRO — PANEL DE ANÁLISIS</div>', unsafe_allow_html=True)

# sidebar
st.sidebar.title("📡 Deportes")
deporte = st.sidebar.radio("Selecciona:", ["🏆 Mundial 2026", "⚽ Fútbol", "🏀 Básquetbol", "🎾 Tenis"])

# Lógica de datos (Si no hay API, usamos este set de datos profesional)
def obtener_datos(deporte):
    # Simulamos datos de mercado
    datos = {
        "Partido": ["Argentina vs Francia", "Brasil vs Inglaterra", "Chile vs Colombia", "España vs Alemania"],
        "Probabilidad Local": ["55%", "60%", "45%", "52%"],
        "Cuota 1": [1.90, 1.85, 2.50, 2.10],
        "Cuota 2": [4.20, 4.50, 2.80, 3.50]
    }
    return pd.DataFrame(datos)

# Mostrar contenido principal
st.subheader(f"📊 Mercado: {deporte}")
df = obtener_datos(deporte)
st.table(df)

# Análisis de mercados secundarios (Córners, Tarjetas)
st.markdown("---")
st.subheader("📋 Análisis de Mercados Secundarios")

# Seleccionamos un partido para el detalle
partido_sel = st.selectbox("Selecciona partido para ver análisis profundo:", df["Partido"].tolist())

if partido_sel:
    col1, col2 = st.columns(2)
    with col1:
        st.info("📉 Córners (Promedio)")
        st.write(f"Pronóstico para {partido_sel}: 9.5 córners totales.")
    with col2:
        st.info("🟨 Tarjetas (Probabilidad)")
        st.write(f"Probabilidad de +4.5 tarjetas: 78%.")

st.warning("⚠️ Nota: Conectado a base de datos de simulación (No requiere API Key).")
