import streamlit as st
import requests
from datetime import datetime

# -----------------------------------------------------------------------------
# CONFIGURACIÓN DE PÁGINA (Layout Amplio)
# -----------------------------------------------------------------------------
st.set_page_config(page_title="BetAnalytics - Estilo Betano", page_icon="🔥", layout="wide", initial_sidebar_state="collapsed")

# -----------------------------------------------------------------------------
# INYECCIÓN DE CSS PERSONALIZADO (HACKEO VISUAL)
# -----------------------------------------------------------------------------
st.markdown("""
<style>
    .block-container { padding-top: 0rem; padding-bottom: 0rem; max-width: 100%; }
    header { visibility: hidden; }
    
    /* Barra Superior Naranja estilo Betano */
    .top-bar {
        background-color: #ff5200; color: white; padding: 15px 20px; font-size: 20px; font-weight: 900;
        display: flex; justify-content: space-between; align-items: center; margin-bottom: 20px; border-radius: 0px 0px 8px 8px;
    }
    .top-bar-links span { margin-left: 20px; font-size: 14px; font-weight: normal; cursor: pointer; }
    
    /* Tarjetas de Partidos Destacados (Oscuras) */
    .match-card {
        background: linear-gradient(135deg, #1a1a1a 0%, #2b2b2b 100%);
        border-radius: 10px; padding: 15px; color: white; margin-bottom: 15px;
        box-shadow: 0 4px 6px rgba(0,0,0,0.3); border-top: 3px solid #ff5200;
    }
    .match-header { font-size: 12px; color: #aaa; margin-bottom: 10px; display: flex; justify-content: space-between;}
    .live-badge { background-color: #ff0000; color: white; padding: 2px 6px; border-radius: 4px; font-weight: bold; font-size: 10px;}
    .teams { font-size: 16px; font-weight: bold; margin-bottom: 15px; line-height: 1.4; }
    
    /* Botones de Cuotas estilo Betano */
    .odds-container { display: flex; gap: 5px; }
    .odds-btn {
        background-color: white; color: #333; flex: 1; text-align: center;
        padding: 8px 5px; border-radius: 4px; font-size: 14px; font-weight: bold; border: 1px solid #ddd;
    }
    .odds-val { color: #00a859; float: right; font-weight: 900;}
    .odds-label { float: left; color: #777; font-size: 12px; margin-top: 2px;}

    /* Lista de Partidos */
    .list-row {
        background-color: #f8f9fa; border: 1px solid #eee; border-radius: 8px;
        padding: 10px 15px; margin-bottom: 8px; display: flex; justify-content: space-between; align-items: center;
    }
    
    /* Panel Derecho */
    .right-panel { background-color: white; border: 1px solid #ddd; border-radius: 8px; padding: 15px; }
    .mentor-header { background-color: #1a1a1a; color: white; padding: 10px; border-radius: 4px 4px 0 0; text-align: center; font-weight: bold; margin-bottom: 15px;}
</style>
""", unsafe_allow_html=True)

# -----------------------------------------------------------------------------
# CONEXIÓN A LA API REAL
# -----------------------------------------------------------------------------
def fetch_live_data(api_key):
    if not api_key: return []
    url = "https://api.the-odds-api.com/v4/sports/soccer_fifa_world_cup/odds/"
    params = {"apiKey": api_key, "regions": "eu", "markets": "h2h", "oddsFormat": "decimal"}
    try:
        response = requests.get(url, params=params)
        return response.json() if response.status_code == 200 else []
    except:
        return []

def extraer_cuotas(partido):
    odds = {"1": "1.15", "X": "3.50", "2": "8.00"} # Por defecto
    try:
        mercados = partido["bookmakers"][0]["markets"][0]["outcomes"]
        for o in mercados:
            if o["name"] == partido["home_team"]: odds["1"] = f"{o['price']:.2f}"
            elif o["name"] == "Draw": odds["X"] = f"{o['price']:.2f}"
            else: odds["2"] = f"{o['price']:.2f}"
    except: pass
    return odds

# -----------------------------------------------------------------------------
# RENDERIZADO DE LA INTERFAZ
# -----------------------------------------------------------------------------
def main():
    # BARRA SUPERIOR (HEADER)
    st.markdown("""
        <div class="top-bar">
            <div>BetAnalytics <span style="font-size:12px; background:white; color:#ff5200; padding:2px 5px; border-radius:4px; margin-left:10px;">PRO</span></div>
            <div class="top-bar-links">
                <span>APUESTAS DEPORTIVAS</span>
                <span style="color:#ffd0b5;">APUESTAS EN VIVO</span>
                <span style="color:#ffd0b5;">CASINO</span>
            </div>
            <div>
                <span style="font-size:14px; border:1px solid white; padding:5px 15px; border-radius:20px; cursor:pointer;">REGISTRO</span>
                <span style="font-size:14px; background:#00a859; color:white; padding:5px 15px; border-radius:20px; margin-left:10px; cursor:pointer;">INGRESAR</span>
            </div>
        </div>
    """, unsafe_allow_html=True)

    # API KEY INPUT EN LA PARTE SUPERIOR IZQUIERDA
    api_key = st.text_input("🔑 Ingresa tu API Key de The Odds para cargar partidos reales:", type="password")

    # LAYOUT DE 3 COLUMNAS
    col_menu, col_main, col_right = st.columns([1.5, 6, 2.5])

    # --- COLUMNA 1: MENÚ LATERAL ---
    with col_menu:
        st.markdown("🎯 **Programación**")
        st.markdown("🏆 **Ganadores**")
        st.markdown("---")
        st.markdown("### COMP. FAVORITAS")
        st.checkbox("🏆 Mundial 2026", value=True)
        st.markdown("### DEPORTES")
        st.markdown("⚽ Fútbol")
        st.markdown("🎾 Tenis")
        st.markdown("🏀 Básquetbol")

    # --- COLUMNA 2: SECCIÓN CENTRAL ---
    with col_main:
        if api_key:
            partidos_reales = fetch_live_data(api_key)
            if partidos_reales:
                # Fila de Tarjetas Destacadas (Primeros 3 partidos)
                cols_cards = st.columns(3)
                for i, match in enumerate(partidos_reales[:3]):
                    odds = extraer_cuotas(match)
                    # Formatear la fecha de la API
                    try:
                        hora = datetime.strptime(match['commence_time'], "%Y-%m-%dT%H:%M:%SZ").strftime("%d/%m %H:%M")
                    except:
                        hora = "Próximamente"

                    with cols_cards[i % 3]:
                        st.markdown(f"""
                        <div class="match-card">
                            <div class="match-header"><span>⏱️ {hora}</span> <span style="background:#ff5200; padding:2px 5px; border-radius:3px; font-size:9px; color:white;">🔥 SUPER CUOTAS</span></div>
                            <div class="teams">{match['home_team']}<br>{match['away_team']}</div>
                            <div class="odds-container">
                                <div class="odds-btn"><span class="odds-label">1</span> <span class="odds-val">{odds['1']}</span></div>
                                <div class="odds-btn"><span class="odds-label">X</span> <span class="odds-val">{odds['X']}</span></div>
                                <div class="odds-btn"><span class="odds-label">2</span> <span class="odds-val">{odds['2']}</span></div>
                            </div>
                        </div>
                        """, unsafe_allow_html=True)

                st.markdown("### 🏆 TODOS LOS PARTIDOS DEL MUNDIAL")
                # Lista de partidos estilo lista
                for match in partidos_reales[3:]:
                    odds = extraer_cuotas(match)
                    st.markdown(f"""
                    <div class="list-row">
                        <div style="width:40%; font-weight:bold; font-size:14px;">
                            {match['home_team']} vs {match['away_team']}
                        </div>
                        <div class="odds-container" style="width:60%;">
                            <div class="odds-btn"><span class="odds-label">1</span> <span class="odds-val">{odds['1']}</span></div>
                            <div class="odds-btn"><span class="odds-label">X</span> <span class="odds-val">{odds['X']}</span></div>
                            <div class="odds-btn"><span class="odds-label">2</span> <span class="odds-val">{odds['2']}</span></div>
                        </div>
                    </div>
                    """, unsafe_allow_html=True)
            else:
                st.info("No hay partidos en la API ahora mismo o la clave es incorrecta.")
        else:
            st.warning("👈 Por favor ingresa tu API Key arriba para cargar la interfaz.")

    # --- COLUMNA 3: PANEL DERECHO (MENTOR) ---
    with col_right:
        st.markdown("""
        <div class="right-panel">
            <div class="mentor-header">⚽ Mentor de Apuestas ⚽</div>
            <p style="font-size:12px; color:#555;">Selecciona el monto que deseas apostar:</p>
            <input type="text" value="5000" style="width:100%; padding:8px; border:1px solid #ccc; border-radius:4px; margin-bottom:10px;">
            <p style="font-size:12px; color:#555;">Selecciona el monto que deseas ganar:</p>
            <div style="display:flex; gap:5px; margin-bottom:10px;">
                <button style="flex:1; padding:5px; border:1px solid #ccc; background:white;">$10k - $50k</button>
                <button style="flex:1; padding:5px; border:1px solid #ccc; background:white;">$50k - $100k</button>
            </div>
            <button style="width:100%; padding:10px; background-color:#1a1a1a; color:white; border:none; border-radius:4px; font-weight:bold;">Generar Boleto</button>
        </div>
        """, unsafe_allow_html=True)

if __name__ == "__main__":
    main()
