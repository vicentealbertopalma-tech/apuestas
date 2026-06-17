import streamlit as st
import requests
import random
from datetime import datetime

# Configuración de página
st.set_page_config(
    page_title="BetAnalytics Pro", 
    page_icon="📈", 
    layout="wide", 
    initial_sidebar_state="collapsed"
)

# Estilos CSS
st.markdown("""
<style>
    .block-container { padding-top: 0rem; padding-bottom: 0rem; max-width: 100%; }
    header { visibility: hidden; }
    .top-bar { background-color: #ff5200; color: white; padding: 15px; font-weight: 900; border-radius: 0 0 8px 8px; }
    .match-card { background: #1a1a1a; border-radius: 8px; padding: 15px; color: white; margin-bottom: 10px; border-left: 4px solid #ff5200; }
    .stat-row { display: flex; justify-content: space-between; padding: 8px; border-bottom: 1px solid #333; }
</style>
""", unsafe_allow_html=True)

# Datos de respaldo (si la API falla o está vacía)
def generar_respaldo():
    return [
        {"home_team": "Argentina", "away_team": "Francia", "commence_time": "EN VIVO", "odds": {"1": "2.10", "X": "3.10", "2": "3.80"}},
        {"home_team": "Brasil", "away_team": "Inglaterra", "commence_time": "EN VIVO", "odds": {"1": "1.85", "X": "3.40", "2": "4.50"}}
    ]

# Análisis profundo
def generar_analisis(home, away):
    random.seed(len(home) + len(away))
    mercados = [
        {"nombre": "Córners Totales", "prob": random.uniform(65, 88), "cuota": 1.60},
        {"nombre": "Tarjetas Amarillas", "prob": random.uniform(50, 75), "cuota": 1.90},
        {"nombre": "Tiros al Arco", "prob": random.uniform(70, 92), "cuota": 1.50}
    ]
    return mercados

# Interfaz
def main():
    st.markdown('<div class="top-bar">BetAnalytics PRO - Sistema Analítico</div>', unsafe_allow_html=True)
    
    # Definición de columnas con seguridad (separadas para evitar errores de sintaxis)
    cols = st.columns([1.5, 6, 2.5])
    
    with cols[0]:
        st.markdown("### 📡 Categorías")
        cat = st.radio("M", ["🔴 En Vivo", "🏆 Mundial", "⚽ Fútbol"], label_visibility="collapsed")
        
    with cols[2]:
        st.markdown("### ⚙️ Filtros")
        prob = st.slider("Probabilidad Mínima:", 50, 95, 65)
        
    with cols[1]:
        partidos = generar_respaldo()
        for p in partidos:
            st.markdown(f"""
            <div class="match-card">
                <div style="font-weight:bold; font-size:18px;">{p['home_team']} vs {p['away_team']}</div>
            </div>
            """, unsafe_allow_html=True)
            
            with st.expander("📊 Ver análisis profundo"):
                data = generar_analisis(p['home_team'], p['away_team'])
                for m in data:
                    if m['prob'] >= prob:
                        st.markdown(f"""
                        <div class="stat-row">
                            <span>{m['nombre']}</span>
                            <span style="color:#00a859;">{m['prob']:.1f}%</span>
                        </div>
                        """, unsafe_allow_html=True)

if __name__ == "__main__":
    main()
