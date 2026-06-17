import streamlit as st
import requests
from datetime import datetime

# -----------------------------------------------------------------------------
# CONFIGURACIÓN DE PÁGINA
# -----------------------------------------------------------------------------
st.set_page_config(page_title="BetAnalytics Pro", page_icon="📈", layout="wide", initial_sidebar_state="collapsed")

# -----------------------------------------------------------------------------
# INYECCIÓN DE CSS (Adaptado para Dark Mode y Modo Analítico)
# -----------------------------------------------------------------------------
st.markdown("""
<style>
    .block-container { padding-top: 0rem; padding-bottom: 0rem; max-width: 100%; }
    header { visibility: hidden; }
    
    /* Barra Superior Analítica */
    .top-bar {
        background-color: #ff5200; color: white; padding: 15px 20px; font-size: 20px; font-weight: 900;
        display: flex; justify-content: space-between; align-items: center; margin-bottom: 20px; border-radius: 0px 0px 8px 8px;
    }
    .top-bar-links span { margin-left: 20px; font-size: 14px; font-weight: normal; color: white; }
    
    /* Tarjetas Destacadas */
    .match-card {
        background: linear-gradient(135deg, #1a1a1a 0%, #2b2b2b 100%);
        border-radius: 10px; padding: 15px; color: white; margin-bottom: 15px;
        box-shadow: 0 4px 6px rgba(0,0,0,0.3); border-top: 3px solid #ff5200;
    }
    .match-header { font-size: 12px; color: #aaa; margin-bottom: 10px; display: flex; justify-content: space-between;}
    .teams { font-size: 16px; font-weight: bold; margin-bottom: 15px; line-height: 1.4; color: white;}
    
    /* Botones de Cuotas Oscuros */
    .odds-container { display: flex; gap: 5px; }
    .odds-btn {
        background-color: #333; color: white; flex: 1; text-align: center;
        padding: 8px 5px; border-radius: 4px; font-size: 14px; font-weight: bold; border: 1px solid #555;
    }
    .odds-val { color: #00a859; float: right; font-weight: 900;}
    .odds-label { float: left; color: #aaa; font-size: 12px; margin-top: 2px;}

    /* Lista de Partidos (Fondo Oscuro para letras blancas) */
    .list-row {
        background-color: #222222; border: 1px solid #444; border-radius: 8px; color: white;
        padding: 12px 15px; margin-bottom: 8px; display: flex; justify-content: space-between; align-items: center;
    }
    
    /* Etiquetas de Análisis */
    .badge-ev { background-color: #00a859; color: white; padding: 4px 8px; border-radius: 4px; font-size: 11px; font-weight: bold; margin-right: 5px;}
    .badge-conf { background-color: #3498db; color: white; padding: 4px 8px; border-radius: 4px; font-size: 11px; font-weight: bold;}
</style>
""", unsafe_allow_html=True)

# -----------------------------------------------------------------------------
# CONEXIÓN A LA API REAL Y MOTOR DE ANÁLISIS
# -----------------------------------------------------------------------------
def fetch_live_data(api_key, sport_key):
    if not api_key: return []
    url = f"https://api.the-odds-api.com/v4/sports/{sport_key}/odds/"
    params = {"apiKey": api_key, "regions": "eu", "markets": "h2h", "oddsFormat": "decimal"}
    try:
        response = requests.get(url, params=params)
        return response.json() if response.status_code == 200 else []
    except:
        return []

def extraer_cuotas(partido):
    odds = {"1": "1.15", "X": "3.50", "2": "8.00"}
    try:
        mercados = partido["bookmakers"][0]["markets"][0]["outcomes"]
        for o in mercados:
            if o["name"] == partido["home_team"]: odds["1"] = f"{o['price']:.2f}"
            elif o["name"] == "Draw": odds["X"] = f"{o['price']:.2f}"
            else: odds["2"] = f"{o['price']:.2f}"
    except: pass
    return odds

def calcular_analisis_falso(cuota):
    """Simula un algoritmo de rentabilidad (EV) basado en la cuota"""
    try:
        c = float(cuota)
        # Algoritmo de simulación para mostrar datos de análisis
        prob_modelo = (1 / c) + 0.035 
        ev = round(((prob_modelo * c) - 1) * 100, 1)
        confianza = min(10, max(1, int(prob_modelo * 12)))
        return ev, confianza
    except:
        return 0, 5

# -----------------------------------------------------------------------------
# RENDERIZADO DE LA INTERFAZ
# -----------------------------------------------------------------------------
def main():
    # BARRA SUPERIOR
    st.markdown("""
        <div class="top-bar">
            <div>BetAnalytics <span style="font-size:12px; background:white; color:#ff5200; padding:2px 5px; border-radius:4px; margin-left:10px;">PRO</span></div>
            <div class="top-bar-links">
                <span>📊 PANEL DE TENDENCIAS</span>
                <span style="color:#ffd0b5;">💥 VALUE BETS</span>
                <span style="color:#ffd0b5;">📈 HISTÓRICO</span>
            </div>
            <div>
                <span style="font-size:14px; background:#00a859; color:white; padding:5px 15px; border-radius:20px; cursor:pointer;">DATOS EN VIVO</span>
            </div>
        </div>
    """, unsafe_allow_html=True)

    api_key = st.text_input("🔑 Ingresa tu API Key de The Odds para rastrear el mercado:", type="password")

    # LAYOUT DE 3 COLUMNAS
    col_menu, col_main, col_right = st.columns([1.5, 6, 2.5])

    # --- COLUMNA 1: MENÚ LATERAL (AHORA FUNCIONAL) ---
    with col_menu:
        st.markdown("### 🏆 DEPORTES")
        st.markdown("Selecciona una liga para analizar:")
        
        deporte_sel = st.radio(
            "Opciones:",
            ["⚽ Fútbol (Premier League)", "⚽ Fútbol (La Liga)", "🏀 Básquetbol (NBA)", "⚾ Béisbol (MLB)", "🏈 Fútbol Americano (NFL)"],
            label_visibility="collapsed"
        )
        
        # Diccionario que conecta el radio button con la API
        sport_keys = {
            "⚽ Fútbol (Premier League)": "soccer_epl",
            "⚽ Fútbol (La Liga)": "soccer_spain_la_liga",
            "🏀 Básquetbol (NBA)": "basketball_nba",
            "⚾ Béisbol (MLB)": "baseball_mlb",
            "🏈 Fútbol Americano (NFL)": "americanfootball_nfl"
        }
        sport_key_actual = sport_keys[deporte_sel]

    # --- COLUMNA 3: PANEL DERECHO (FILTROS NATIVOS DE STREAMLIT) ---
    with col_right:
        st.markdown("### ⚙️ FILTROS DE TRADING")
        st.info("Ajusta el algoritmo para filtrar los partidos de la lista central.")
        
        filtro_ev = st.slider("Valor Esperado (EV %) Mínimo:", min_value=-5.0, max_value=15.0, value=0.0, step=0.5)
        filtro_confianza = st.slider("Confianza Mínima (1-10):", min_value=1, max_value=10, value=4)
        
        st.markdown("---")
        st.metric(label="Deporte Analizado", value=deporte_sel.split(" ")[0] + " " + deporte_sel.split(" ")[1])

    # --- COLUMNA 2: SECCIÓN CENTRAL (PARTIDOS) ---
    with col_main:
        if api_key:
            with st.spinner(f"Analizando mercado de {deporte_sel}..."):
                partidos_reales = fetch_live_data(api_key, sport_key_actual)
            
            if partidos_reales:
                # 1. Tarjetas Superiores (Top 3 partidos)
                cols_cards = st.columns(3)
                for i, match in enumerate(partidos_reales[:3]):
                    odds = extraer_cuotas(match)
                    try:
                        hora = datetime.strptime(match['commence_time'], "%Y-%m-%dT%H:%M:%SZ").strftime("%d/%m %H:%M")
                    except:
                        hora = "Próximamente"

                    with cols_cards[i % 3]:
                        st.markdown(f"""
                        <div class="match-card">
                            <div class="match-header"><span>⏱️ {hora}</span> <span style="background:#ff5200; padding:2px 5px; border-radius:3px; font-size:9px; color:white;">🔥 ALTO VALOR</span></div>
                            <div class="teams">{match['home_team']}<br>{match['away_team']}</div>
                            <div class="odds-container">
                                <div class="odds-btn"><span class="odds-label">1</span> <span class="odds-val">{odds['1']}</span></div>
                                <div class="odds-btn"><span class="odds-label">X</span> <span class="odds-val">{odds['X']}</span></div>
                                <div class="odds-btn"><span class="odds-label">2</span> <span class="odds-val">{odds['2']}</span></div>
                            </div>
                        </div>
                        """, unsafe_allow_html=True)

                st.markdown(f"### 📋 MATRIZ DE OPORTUNIDADES: {deporte_sel.upper()}")
                
                # 2. Lista Analítica Completa (Aplicando los filtros del panel derecho)
                partidos_mostrados = 0
                for match in partidos_reales[3:]:
                    odds = extraer_cuotas(match)
                    
                    # Generamos el análisis para el equipo local
                    ev, confianza = calcular_analisis_falso(odds['1'])
                    
                    # Aplicamos los filtros del slider
                    if ev >= filtro_ev and confianza >= filtro_confianza:
                        partidos_mostrados += 1
                        ev_clase = "badge-ev" if ev > 0 else "badge-ev-neg"
                        
                        st.markdown(f"""
                        <div class="list-row">
                            <div style="width:45%; font-weight:bold; font-size:14px;">
                                {match['home_team']} vs {match['away_team']}<br>
                                <span class="{ev_clase}">EV: {ev}%</span>
                                <span class="badge-conf">Confianza: {confianza}/10</span>
                            </div>
                            <div class="odds-container" style="width:55%;">
                                <div class="odds-btn"><span class="odds-label">1</span> <span class="odds-val">{odds['1']}</span></div>
                                <div class="odds-btn"><span class="odds-label">X</span> <span class="odds-val">{odds['X']}</span></div>
                                <div class="odds-btn"><span class="odds-label">2</span> <span class="odds-val">{odds['2']}</span></div>
                            </div>
                        </div>
                        """, unsafe_allow_html=True)
                
                if partidos_mostrados == 0:
                    st.warning("⚠️ Ningún partido cumple con los filtros de Valor Esperado y Confianza actuales. Ajusta los sliders a la derecha.")
            else:
                st.info(f"No hay partidos disponibles ahora mismo para {deporte_sel} o la liga no está en temporada.")
        else:
            st.warning("👈 Por favor ingresa tu API Key arriba para escanear el mercado.")

if __name__ == "__main__":
    main()
