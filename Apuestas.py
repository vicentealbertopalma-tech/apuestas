import streamlit as st
import pandas as pd

st.set_page_config(page_title="BetAnalytics Pro", layout="wide")

# Barra Superior
st.markdown("""
<style>
    .top-bar { background-color: #ff5200; color: white; padding: 20px; font-weight: 900; font-size: 24px; border-radius: 0 0 10px 10px; }
    .metric-card { background: #1a1a1a; padding: 20px; border-radius: 10px; border-top: 4px solid #ff5200; }
</style>
<div class="top-bar">BETANALYTICS PRO — COPA DEL MUNDO 2026</div>
""", unsafe_allow_html=True)

# Métricas Globales
c1, c2, c3, c4 = st.columns(4)
c1.metric("Partidos Hoy", "54")
c2.metric("Mercados Analizados", "432")
c3.metric("Value Bets", "404")
c4.metric("Confianza", "7.6/10")

st.markdown("---")

# Filtros
col_izq, col_der = st.columns([1, 3])
with col_izq:
    st.subheader("⚙️ Filtros de Trading")
    st.slider("Nivel de Confianza", 1, 10, 5)
    st.checkbox("Filtrar solo Value Bets (EV > 0)")

with col_der:
    st.subheader("🏆 Matriz de Oportunidades")
    # Tabla de ejemplo
    data = {
        "Partido": ["Argentina vs Algeria", "Portugal vs Congo"],
        "Mercado": ["Más 0.5 Goles", "Más 7.5 Córners"],
        "Probabilidad": ["90%", "91%"],
        "EV": ["+0.026", "+0.229"]
    }
    st.table(pd.DataFrame(data))
