import streamlit as st
import pandas as pd

st.set_page_config(page_title="BetAnalytics Pro", layout="wide")

# Estilo para fondo oscuro y colores profesionales
st.markdown("""
<style>
    .main { background-color: #0e1117; }
    .stApp { background-color: #0e1117; }
    .header-box { background-color: #ff5200; padding: 20px; border-radius: 10px; color: white; text-align: center; margin-bottom: 20px;}
    .card { background-color: #1a1a1a; padding: 15px; border-radius: 10px; margin-bottom: 10px; border-left: 5px solid #ff5200; }
</style>
""", unsafe_allow_html=True)

# Encabezado
st.markdown('<div class="header-box"><h1>BETANALYTICS PRO — COPA DEL MUNDO 2026</h1></div>', unsafe_allow_html=True)

# Datos de muestra (Simulando partidos en vivo)
data = {
    "Partido": ["Argentina vs Francia", "Brasil vs Inglaterra", "Chile vs Colombia", "España vs Alemania"],
    "Estado": ["🔴 En Vivo 65'", "🔴 En Vivo 12'", "⏱️ Mañana 16:00", "⏱️ Mañana 20:00"],
    "Prob. Local": ["55%", "60%", "45%", "52%"],
    "Cuota": ["1.90", "1.85", "2.50", "2.10"]
}
df = pd.DataFrame(data)

# Layout: Izquierda (Filtros), Centro (Partidos), Derecha (Análisis)
col1, col2, col3 = st.columns([1, 2, 1.5])

with col1:
    st.subheader("⚙️ Filtros")
    filtro = st.radio("Selecciona categoría:", ["🔴 En Vivo", "🏆 Mundial", "⚽ Fútbol"])
    st.slider("Nivel de Confianza", 1, 10, 5)

with col2:
    st.subheader("📡 Partidos en Directo")
    for i in range(len(df)):
        with st.container():
            st.markdown(f"""
            <div class="card">
                <b>{df.loc[i, 'Partido']}</b><br>
                <span style="color: #ff5200;">{df.loc[i, 'Estado']}</span>
            </div>
            """, unsafe_allow_html=True)

with col3:
    st.subheader("📊 Análisis Profundo")
    partido_sel = st.selectbox("Elegir partido para analizar:", df["Partido"].tolist())
    
    # Análisis dinámico basado en la selección
    st.write(f"### Análisis de {partido_sel}")
    st.progress(85)
    st.write("📈 **Córners:** 85% probabilidad")
    st.progress(70)
    st.write("🟨 **Tarjetas:** 70% probabilidad")
    st.success("Justificación estadística: Alta intensidad en fase de grupos.")
