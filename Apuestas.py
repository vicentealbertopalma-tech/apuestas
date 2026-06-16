import datetime
import sqlite3
import numpy as np
import pandas as pd
import streamlit as st

# -----------------------------------------------------------------------------
# CONFIGURACIÓN DE LA PÁGINA 
# -----------------------------------------------------------------------------
st.set_page_config(
    page_title="BetAnalytics Pro - Panel de Probabilidades",
    page_icon="⚽",
    layout="wide",
)

# -----------------------------------------------------------------------------
# MÓDULO 1: RECOLECCIÓN DE DATOS (Simulación Estructurada de Producción)
# -----------------------------------------------------------------------------
class SportDataFetcher:
    def __init__(self):
        pass

    def fetch_live_fixtures(self) -> pd.DataFrame:
        partidos = [
            {"id": 101, "liga": "Premier League", "local": "Liverpool", "visitante": "Chelsea", "hora": "16:00"},
            {"id": 102, "liga": "LaLiga", "local": "Real Madrid", "visitante": "Barcelona", "hora": "17:00"},
            {"id": 103, "liga": "Serie A", "local": "Inter", "visitante": "Juventus", "hora": "14:45"},
            {"id": 104, "liga": "Bundesliga", "local": "Bayern Munich", "visitante": "Dortmund", "hora": "13:30"},
            {"id": 105, "liga": "Champions League", "local": "Man City", "visitante": "PSG", "hora": "16:00"},
        ]
        return pd.DataFrame(partidos)

    def fetch_historical_stats(self, equipo: str, es_local: bool) -> dict:
        np.random.seed(sum(ord(c) for c in equipo))
        goles_favor = np.random.uniform(1.8, 3.0) if es_local else np.random.uniform(1.2, 2.2)
        goles_contra = np.random.uniform(0.5, 1.2) if es_local else np.random.uniform(1.0, 1.8)

        return {
            "promedio_goles_f": round(goles_favor, 2),
            "promedio_goles_c": round(goles_contra, 2),
            "promedio_corners": round(np.random.uniform(5.5, 8.5), 2),
            "promedio_tarjetas": round(np.random.uniform(1.2, 2.8), 2),
            "porcentaje_mas_05": round(np.random.uniform(85, 98), 2),
            "porcentaje_mas_15": round(np.random.uniform(65, 88), 2),
            "tiros_al_arco": round(np.random.uniform(4.5, 7.0), 2),
            "forma_reciente": np.random.choice([0.8, 0.9, 0.7, 0.6]),
        }

    def fetch_live_odds(self, partido_id: int) -> dict:
        np.random.seed(partido_id)
        return {
            "Mas 0.5 Goles": round(np.random.uniform(1.10, 1.18), 2),
            "Mas 1.5 Goles": round(np.random.uniform(1.28, 1.45), 2),
            "Doble Oportunidad": round(np.random.uniform(1.15, 1.35), 2),
            "Mas 7.5 Corners": round(np.random.uniform(1.30, 1.55), 2),
            "Ambos Marca un Tiro al Arco": round(np.random.uniform(1.12, 1.25), 2),
        }

# -----------------------------------------------------------------------------
# MÓDULO 2: MOTOR ESTADÍSTICO
# -----------------------------------------------------------------------------
class BetAnalyticsEngine:
    def __init__(self):
        pass

    def calcular_poisson_prob(self, lam: float, k: int) -> float:
        prob = 0.0
        for i in range(k):
            # Usamos una aproximación directa para evitar problemas de tipos de datos
            factorial = 1
            for j in range(1, i + 1):
                factorial *= j
            prob += (np.exp(-lam) * (lam**i)) / factorial
        return prob

    def analizar_partido(self, partido: dict, data_fetcher: SportDataFetcher) -> list:
        stats_local = data_fetcher.fetch_historical_stats(partido["local"], es_local=True)
        stats_vis = data_fetcher.fetch_historical_stats(partido["visitante"], es_local=False)
        cuotas = data_fetcher.fetch_live_odds(partido["id"])

        recomendaciones = []

        lambda_goles = (stats_local["promedio_goles_f"] + stats_vis["promedio_goles_c"]) / 2 + (stats_vis["promedio_goles_f"] + stats_local["promedio_goles_c"]) / 2

        prob_menos_05 = self.calcular_poisson_prob(lambda_goles, 1)
        prob_mas_05 = max(0.0, 1.0 - prob_menos_05)
        
        prob_menos_15 = self.calcular_poisson_prob(lambda_goles, 2)
        prob_mas_15 = max(0.0, 1.0 - prob_menos_15)

        mercados_evaluar = [
            {
                "mercado": "Más de 0.5 Goles",
                "prob": prob_mas_05,
                "cuota": cuotas["Mas 0.5 Goles"],
                "justificacion": f"Expectativa conjunta de {lambda_goles:.2f} goles. Local registra +0.5 en {stats_local['porcentaje_mas_05']}% de sus cruces.",
            },
            {
                "mercado": "Más de 1.5 Goles",
                "prob": prob_mas_15,
                "cuota": cuotas["Mas 1.5 Goles"],
                "justificacion": f"Frecuencia combinada alta. {partido['local']} promedia {stats_local['promedio_goles_f']} anotados en casa.",
            },
            {
                "mercado": "Más de 7.5 Corners",
                "prob": (stats_local["promedio_corners"] + stats_vis["promedio_corners"]) / 16,
                "cuota": cuotas["Mas 7.5 Corners"],
                "justificacion": f"Suma de promedios de tiros de esquina igual a {stats_local['promedio_corners'] + stats_vis['promedio_corners']:.1f} por encuentro.",
            },
        ]

        for m in mercados_evaluar:
            prob_final = min(0.99, max(0.40, m["prob"]))
            ev = (prob_final * m["cuota"]) - 1

            confianza = int((stats_local["forma_reciente"] + stats_vis["forma_reciente"]) * 5 + (prob_final * 3))
            confianza = min(10, max(1, confianza))

            recomendaciones.append({
                "Partido": f"⚽ {partido['local']} vs {partido['visitante']}",
                "Liga": partido["liga"],
                "Mercado Recomendado": m["mercado"],
                "Probabilidad Estimada": f"{prob_final * 100:.1f}%",
                "Cuota Actual": m["cuota"],
                "Valor Esperado (EV)": round(ev, 3),
                "Nivel de Confianza": confianza,
                "Justificación Estadística": m["justificacion"],
                "es_value_bet": ev > 0,
            })

        return recomendaciones

# -----------------------------------------------------------------------------
# MÓDULO 3: BASE DE DATOS
# -----------------------------------------------------------------------------
def init_db():
    conn = sqlite3.connect("analytics_storage.db")
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS registro_analisis (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            fecha TEXT,
            partido TEXT,
            mercado TEXT,
            probabilidad REAL,
            cuota REAL,
            ev REAL,
            confianza INTEGER
        )
    """)
    conn.commit()
    conn.close()

def guardar_analisis_db(datos: list):
    conn = sqlite3.connect("analytics_storage.db")
    cursor = conn.cursor()
    fecha_hoy = datetime.date.today().strftime("%Y-%m-%d")
    for d in datos:
        cursor.execute("""
            INSERT INTO registro_analisis (fecha, partido, mercado, probabilidad, cuota, ev, confianza)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """, (
            fecha_hoy,
            d["Partido"],
            d["Mercado Recomendado"],
            float(d["Probabilidad Estimada"].replace("%", "")),
            d["Cuota Actual"],
            d["Valor Esperado (EV)"],
            d["Nivel de Confianza"],
        ))
    conn.commit()
    conn.close()

# -----------------------------------------------------------------------------
# MÓDULO 4: INTERFAZ DE USUARIO 
# -----------------------------------------------------------------------------
def main():
    init_db()
    fetcher = SportDataFetcher()
    engine = BetAnalyticsEngine()

    st.title("🍊 BETANALYTICS SPORT ENGINE")
    st.subheader("Algoritmo de Alta Probabilidad y Valor Esperado")
    st.markdown("---")

    st.sidebar.header("⚙️ PANEL DE CONTROL")
    filtro_liga = st.sidebar.multiselect(
        "Seleccionar Ligas",
        options=["Premier League", "LaLiga", "Serie A", "Bundesliga", "Champions League"],
        default=["Premier League", "LaLiga", "Champions League"],
    )

    min_confianza = st.sidebar.slider("Nivel de Confianza Mínimo", min_value=1, max_value=10, value=5)
    solo_value_bets = st.sidebar.checkbox("Mostrar solo Value Bets (EV > 0)", value=False)

    partidos_hoy = fetcher.fetch_live_fixtures()
    todos_analisis = []

    for _, row in partidos_hoy.iterrows():
        if row["liga"] in filtro_liga:
            analisis_partido = engine.analizar_partido(row, fetcher)
            todos_analisis.extend(analisis_partido)

    if todos_analisis:
        df_analisis = pd.DataFrame(todos_analisis)

        if solo_value_bets:
            df_analisis = df_analisis[df_analisis["es_value_bet"] == True]
        df_analisis = df_analisis[df_analisis["Nivel de Confianza"] >= min_confianza]

        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.metric("Partidos del Día", len(partidos_hoy))
        with col2:
            st.metric("Oportunidades", len(df_analisis))
        with col3:
            value_bets_count = df_analisis["es_value_bet"].sum() if not df_analisis.empty else 0
            st.metric("💥 Value Bets", int(value_bets_count))
        with col4:
            prom_conf = df_analisis["Nivel de Confianza"].mean() if not df_analisis.empty else 0
            st.metric("🎯 Confianza Promedio", f"{prom_conf:.1f}/10")

        st.markdown("### 📋 Cuadro de Recomendaciones")

        if not df_analisis.empty:
            try:
                guardar_analisis_db(todos_analisis)
            except Exception:
                pass

            df_display = df_analisis.drop(columns=["es_value_bet", "Liga"])
            df_display = df_display[[
                "Partido", "Mercado Recomendado", "Probabilidad Estimada", 
                "Cuota Actual", "Valor Esperado (EV)", "Nivel de Confianza", "Justificación Estadística"
            ]]

            st.dataframe(df_display, use_container_width=True, height=400)
        else:
            st.info("No hay mercados que cumplan estrictamente los filtros actuales.")
    else:
        st.info("Selecciona al menos una liga en el panel izquierdo.")

    st.markdown("---")
    if st.button("🔄 Actualizar en Tiempo Real"):
        st.rerun()

if __name__ == "__main__":
    main()
