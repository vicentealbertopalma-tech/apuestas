import datetime
import sqlite3
import numpy as np
import pandas as pd
import sklearn
import streamlit as st
import xgboost as xgb

# -----------------------------------------------------------------------------
# CONFIGURACIÓN DE LA PÁGINA (Estilo Dark / Betano Premium)
# -----------------------------------------------------------------------------
st.set_page_config(
    page_title="BetAnalytics Pro - Panel de Probabilidades",
    page_icon="⚽",
    layout="wide",
)

# Inyección de CSS para emular la interfaz limpia y compacta de Betano
st.markdown(
    """
    <style>
    .reportview-container { background: #1A1E27; }
    .stMetric { background-color: #222834; padding: 15px; border-radius: 8px; border-left: 5px solid #FF7900; }
    div[data-testid="stDataFrame"] div { font-family: monospace; }
    h1, h2, h3 { color: #FFFFFF; }
    .badge-value { background-color: #2E7D32; color: white; padding: 4px 8px; border-radius: 4px; font-weight: bold; }
    .badge-confidence { background-color: #1565C0; color: white; padding: 4px 8px; border-radius: 4px; font-weight: bold; }
    </style>
    """,
    unsafe_allowed_html=True,
)


# -----------------------------------------------------------------------------
# MÓDULO 1: RECOLECCIÓN DE DATOS (Simulación Estructurada de Producción)
# -----------------------------------------------------------------------------
class SportDataFetcher:
    """Maneja la adquisición de datos en tiempo real e históricos."""

    def __init__(self):
        # En producción, aquí guardarías las API Keys (e.g., self.api_key = "...")
        pass

    def fetch_live_fixtures(self) -> pd.DataFrame:
        """Simula la llegada de partidos del día desde API-Football."""
        partidos = [
            {
                "id": 101,
                "liga": "Premier League",
                "local": "Liverpool",
                "visitante": "Chelsea",
                "hora": "16:00",
            },
            {
                "id": 102,
                "liga": "LaLiga",
                "local": "Real Madrid",
                "visitante": "Barcelona",
                "hora": "17:00",
            },
            {
                "id": 103,
                "liga": "Serie A",
                "local": "Inter",
                "visitante": "Juventus",
                "hora": "14:45",
            },
            {
                "id": 104,
                "liga": "Bundesliga",
                "local": "Bayern Munich",
                "visitante": "Dortmund",
                "hora": "13:30",
            },
            {
                "id": 105,
                "liga": "Champions League",
                "local": "Man City",
                "visitante": "PSG",
                "hora": "16:00",
            },
        ]
        return pd.DataFrame(partidos)

    def fetch_historical_stats(self, equipo: str, es_local: bool) -> dict:
        """Simula las estadísticas de los últimos 10 partidos."""
        # Datos controlados basados en el perfil del equipo para que el modelo tenga sentido numérico
        np.random.seed(sum(ord(c) for c in equipo))

        goles_favor = (
            np.random.uniform(1.8, 3.0) if es_local else np.random.uniform(1.2, 2.2)
        )
        goles_contra = (
            np.random.uniform(0.5, 1.2) if es_local else np.random.uniform(1.0, 1.8)
        )

        return {
            "promedio_goles_f": round(goles_favor, 2),
            "promedio_goles_c": round(goles_contra, 2),
            "promedio_corners": round(np.random.uniform(5.5, 8.5), 2),
            "promedio_tarjetas": round(np.random.uniform(1.2, 2.8), 2),
            "porcentaje_mas_05": round(np.random.uniform(85, 98), 2),
            "porcentaje_mas_15": round(np.random.uniform(65, 88), 2),
            "tiros_al_arco": round(np.random.uniform(4.5, 7.0), 2),
            "forma_reciente": np.random.choice(
                [0.8, 0.9, 0.7, 0.6]
            ),  # % de puntos obtenidos
        }

    def fetch_live_odds(self, partido_id: int) -> dict:
        """Simula cuotas en tiempo real provenientes de The Odds API."""
        # Cuotas base lógicas para mercados estables de bajo riesgo
        np.random.seed(partido_id)
        return {
            "Mas 0.5 Goles": round(np.random.uniform(1.10, 1.18), 2),
            "Mas 1.5 Goles": round(np.random.uniform(1.28, 1.45), 2),
            "Doble Oportunidad": round(np.random.uniform(1.15, 1.35), 2),
            "Mas 7.5 Corners": round(np.random.uniform(1.30, 1.55), 2),
            "Ambos Marca un Tiro al Arco": round(
                np.random.uniform(1.12, 1.25), 2
            ),
        }


# -----------------------------------------------------------------------------
# MÓDULO 2: MOTOR ESTADÍSTICO Y MACHINE LEARNING
# -----------------------------------------------------------------------------
class BetAnalyticsEngine:
    """Procesa métricas, calcula probabilidades y detecta Value Bets."""

    def __init__(self):
        # En una app real, aquí cargarías un modelo entrenado previamente (.pkl)
        # Usaremos una aproximación matemática sólida basada en distribución y frecuencias históricas
        pass

    def calcular_poisson_prob(self, lam: float, k: int) -> float:
        """Calcula la probabilidad de Poisson para menos de k goles."""
        prob = 0.0
        for i in range(k):
            prob += (np.exp(-lam) * (lam**i)) / np.math.factorial(i)
        return prob

    def analizar_partido(self, partido: dict, data_fetcher: SportDataFetcher) -> list:
        stats_local = data_fetcher.fetch_historical_stats(
            partido["local"], es_local=True
        )
        stats_vis = data_fetcher.fetch_historical_stats(
            partido["visitante"], es_local=False
        )
        cuotas = data_fetcher.fetch_live_odds(partido["id"])

        recomendaciones = []

        # EXPECTATIVA DE GOLES (Distribución combinada)
        lambda_goles = (
            stats_local["promedio_goles_f"] + stats_vis["promedio_goles_c"]
        ) / 2 + (stats_vis["promedio_goles_f"] + stats_local["promedio_goles_c"]) / 2

        # Mercado 1: Más de 0.5 Goles
        prob_menos_05 = self.calcular_poisson_prob(lambda_goles, 1)
        prob_mas_05 = max(0.0, 1.0 - prob_menos_05)
        
        # Mercado 2: Más de 1.5 Goles
        prob_menos_15 = self.calcular_poisson_prob(lambda_goles, 2)
        prob_mas_15 = max(0.0, 1.0 - prob_menos_15)

        mercados_evaluar = [
            {
                "mercado": "Más de 0.5 Goles",
                "prob": prob_mas_05,
                "cuota": cuotas["Mas 0.5 Goles"],
                "justificacion": f"Expectativa conjunta de {lambda_goles:.2f} goles. Historial local registra +0.5 goles en {stats_local['porcentaje_mas_05']}% de sus cruces.",
            },
            {
                "mercado": "Más de 1.5 Goles",
                "prob": prob_mas_15,
                "cuota": cuotas["Mas 1.5 Goles"],
                "justificacion": f"Frecuencia combinada alta. {partido['local']} promedia {stats_local['promedio_goles_f']} anotados en casa.",
            },
            {
                "mercado": "Más de 7.5 Corners",
                "prob": (
                    stats_local["promedio_corners"] + stats_vis["promedio_corners"]
                )
                / 16,  # Normalización empírica
                "cuota": cuotas["Mas 7.5 Corners"],
                "justificacion": f"Suma de promedios de tiros de esquina igual a {stats_local['promedio_corners'] + stats_vis['promedio_corners']:.1f} por encuentro.",
            },
        ]

        for m in mercados_evaluar:
            prob_final = min(
                0.99, max(0.40, m["prob"])
            )  # Bounded para realismo de mercado
            ev = (prob_final * m["cuota"]) - 1

            # Nivel de confianza ponderando la forma reciente de ambos y la estabilidad de los datos
            confianza = int(
                (stats_local["forma_reciente"] + stats_vis["forma_reciente"])
                * 5
                + (prob_final * 3)
            )
            confianza = min(10, max(1, confianza))

            recomendaciones.append(
                {
                    "Partido": f"⚽ {partido['local']} vs {partido['visitante']}",
                    "Liga": partido["liga"],
                    "Mercado Recomendado": m["mercado"],
                    "Probabilidad Estimada": f"{prob_final * 100:.1f}%",
                    "Cuota Actual": m["cuota"],
                    "Valor Esperado (EV)": round(ev, 3),
                    "Nivel de Confianza": confianza,
                    "Justificación Estadística": m["justificacion"],
                    "es_value_bet": ev > 0,
                }
            )

        return recomendaciones


# -----------------------------------------------------------------------------
# MÓDULO 3: BASE DE DATOS (Persistencia Local)
# -----------------------------------------------------------------------------
def init_db():
    conn = sqlite3.connect("analytics_storage.db")
    cursor = conn.cursor()
    cursor.execute(
        """
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
    """
    )
    conn.commit()
    conn.close()


def guardar_analisis_db(datos: list):
    conn = sqlite3.connect("analytics_storage.db")
    cursor = conn.cursor()
    fecha_hoy = datetime.date.today().strftime("%Y-%m-%d")
    for d in datos:
        cursor.execute(
            """
            INSERT INTO registro_analisis (fecha, partido, mercado, probabilidad, cuota, ev, confianza)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """,
            (
                fecha_hoy,
                d["Partido"],
                d["Mercado Recomendado"],
                float(d["Probabilidad Estimada"].replace("%", "")),
                d["Cuota Actual"],
                d["Valor Esperado (EV)"],
                d["Nivel de Confianza"],
            ),
        )
    conn.commit()
    conn.close()


# -----------------------------------------------------------------------------
# MÓDULO 4: INTERFAZ DE USUARIO (Diseño Betano UX)
# -----------------------------------------------------------------------------
def main():
    init_db()
    fetcher = SportDataFetcher()
    engine = BetAnalyticsEngine()

    # HEADER ESTILO CASA DE APUESTAS
    st.title("🍊 BETANALYTICS SPORT ENGINE")
    st.subheader(
        "Algoritmo de Alta Probabilidad y Valor Esperado para Mercados Estables"
    )
    st.markdown("---")

    # BARRA LATERAL - FILTROS COMPACTOS
    st.sidebar.header("⚙️ PANEL DE CONTROL")
    filtro_liga = st.sidebar.multiselect(
        "Seleccionar Ligas",
        options=["Premier League", "LaLiga", "Serie A", "Bundesliga", "Champions League"],
        default=["Premier League", "LaLiga", "Champions League"],
    )

    min_confianza = st.sidebar.slider(
        "Nivel de Confianza Mínimo", min_value=1, max_value=10, value=6
    )
    solo_value_bets = st.sidebar.checkbox("Mostrar solo Value Bets (EV > 0)", value=True)

    # PIPELINE DE PROCESAMIENTO
    partidos_hoy = fetcher.fetch_live_fixtures()
    todos_analisis = []

    for _, row in partidos_hoy.iterrows():
        if row["liga"] in filtro_liga:
            analisis_partido = engine.analizar_partido(row, fetcher)
            todos_analisis.extend(analisis_partido)

    df_analisis = pd.DataFrame(todos_analisis)

    # FILTRADO DE DATOS SEGÚN ENTRADAS DEL SIDEBAR
    if not df_analisis.empty:
        if solo_value_bets:
            df_analisis = df_analisis[df_analisis["es_value_bet"] == True]
        df_analisis = df_analisis[df_analisis["Nivel de Confianza"] >= min_confianza]

    # SECCIÓN DE MÉTRICAS CLAVE (KPIs superiores)
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("Partidos del Día", len(partidos_hoy))
    with col2:
        st.metric("Oportunidades Filtradas", len(df_analisis) if not df_analisis.empty else 0)
    with col3:
        value_bets_count = (
            df_analisis["es_value_bet"].sum() if not df_analisis.empty else 0
        )
        st.metric("💥 Value Bets Detectadas", int(value_bets_count))
    with col4:
        prom_conf = (
            df_analisis["Nivel de Confianza"].mean()
            if not df_analisis.empty
            else 0
        )
        st.metric("🎯 Confianza Promedio", f"{prom_conf:.1f}/10")

    st.markdown("### 📋 Cuadro de Recomendaciones Filtradas")

    if not df_analisis.empty:
        # Almacenamos temporalmente en la BD para el histórico antes de limpiar columnas estéticas
        try:
            guardar_analisis_db(todos_analisis)
        except Exception:
            pass

        # Preparar DataFrame final para visualización limpia
        df_display = df_analisis.drop(columns=["es_value_bet", "Liga"])

        # Reordenar columnas para legibilidad óptima
        df_display = df_display[
            [
                "Partido",
                "Mercado Recomendado",
                "Probabilidad Estimada",
                "Cuota Actual",
                "Valor Esperado (EV)",
                "Nivel de Confianza",
                "Justificación Estadística",
            ]
        ]

        # Renderizar la tabla interactiva con formato condicional nativo de Streamlit
        st.dataframe(
            df_display.style.background_gradient(
                subset=["Valor Esperado (EV)"], cmap="Greens"
            ).background_gradient(subset=["Nivel de Confianza"], cmap="Blues"),
            use_container_width=True,
            height=350,
        )
    else:
        st.info(
            "No se encontraron mercados de alta probabilidad que cumplan exactamente los filtros seleccionados en este momento."
        )

    # BOTÓN DE RE-EJECUCIÓN / ACTUALIZACIÓN EN VIVO
    st.markdown("---")
    if st.button("🔄 Forzar actualización de datos en Tiempo Real"):
        st.rerun()


if __name__ == "__main__":
    main()
