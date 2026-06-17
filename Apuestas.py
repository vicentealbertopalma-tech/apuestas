import numpy as np
import pandas as pd
import requests
import streamlit as st

# -----------------------------------------------------------------------------
# CONFIGURACIÓN DE LA PÁGINA
# -----------------------------------------------------------------------------
st.set_page_config(
    page_title="BetAnalytics Pro",
    page_icon="🏆",
    layout="wide",
)

# -----------------------------------------------------------------------------
# MÓDULO 1: RECOLECCIÓN DE DATOS REALES (The Odds API)
# -----------------------------------------------------------------------------
class SportDataFetcher:
    """
    Trae cuotas reales en vivo desde The Odds API.
    No genera datos de respaldo simulados: si no hay API Key válida o la API
    no devuelve nada, se informa claramente al usuario en lugar de mostrar
    partidos o cuotas inventadas.
    """

    def __init__(self, api_key: str):
        self.api_key = api_key
        self.sports_map = {
            "⚽ Fútbol (Mundial)": "soccer_fifa_world_cup",
            "🏀 Básquetbol (NBA)": "basketball_nba",
            "⚾ Béisbol (MLB)": "baseball_mlb",
            "🏈 Fútbol Americano (NFL)": "americanfootball_nfl",
        }
        # Mercados reales soportados por The Odds API para cada deporte.
        # h2h = ganador del partido (1X2 en fútbol, moneyline en el resto)
        # totals = más/menos goles o puntos totales
        # spreads = hándicap
        self.markets_por_deporte = "h2h,totals,spreads"

    def fetch_live_data(self, deporte_seleccionado: str):
        """
        Devuelve (datos, error). Si error no es None, datos es None.
        Usamos dos regiones (eu, uk) para tener varias casas de apuestas y
        poder calcular un consenso de mercado confiable. Más regiones = más
        casas comparadas, pero también más costo de cuota en la API.
        """
        sport_key = self.sports_map.get(deporte_seleccionado)
        if not sport_key:
            return None, "Deporte no reconocido."

        if not self.api_key:
            return None, "Ingresa tu API Key de The Odds API para ver datos reales del mercado."

        url = f"https://api.the-odds-api.com/v4/sports/{sport_key}/odds/"
        params = {
            "apiKey": self.api_key,
            "regions": "eu,uk",
            "markets": self.markets_por_deporte,
            "oddsFormat": "decimal",
        }

        try:
            response = requests.get(url, params=params, timeout=10)
        except requests.exceptions.RequestException as e:
            return None, f"No se pudo conectar con The Odds API: {e}"

        if response.status_code != 200:
            return None, f"The Odds API respondió con error {response.status_code}: {response.text[:200]}"

        data = response.json()
        if not data:
            return None, "La API no devolvió partidos para este deporte en este momento (puede que no haya eventos próximos)."

        return data, None


# -----------------------------------------------------------------------------
# MÓDULO 2: MOTOR ESTADÍSTICO — CONSENSO DE MERCADO (DEVIG)
# -----------------------------------------------------------------------------
class BetAnalyticsEngine:
    """
    Calcula probabilidades "justas" quitando el margen de la casa (vig) de
    las cuotas de múltiples bookmakers, y compara esa probabilidad contra la
    mejor cuota disponible para detectar Valor Esperado (EV) positivo real.

    Esto es un método estándar de trading deportivo (no-vig / consenso de
    mercado): si varias casas coinciden en que un resultado tiene cierta
    probabilidad real, y una casa específica ofrece una cuota mejor que esa
    probabilidad implica, ahí hay una ventaja matemática genuina.
    """

    MIN_CASAS = 2  # mínimo de bookmakers necesarios para confiar en un consenso

    @staticmethod
    def _devig(prices: list) -> list:
        implicitas = [1.0 / p for p in prices]
        total = sum(implicitas)
        return [p / total for p in implicitas]

    @staticmethod
    def _nivel_acuerdo(std: float) -> str:
        if std < 0.02:
            return "Alto"
        elif std < 0.05:
            return "Medio"
        return "Bajo"

    def _consenso_h2h(self, bookmakers: list) -> dict:
        """Probabilidad justa de cada resultado (ganador local/empate/visitante)."""
        probs_por_resultado = {}
        mejor_por_resultado = {}

        for bk in bookmakers:
            mercado = next((m for m in bk.get("markets", []) if m["key"] == "h2h"), None)
            if not mercado or len(mercado.get("outcomes", [])) < 2:
                continue

            nombres = [o["name"] for o in mercado["outcomes"]]
            precios = [o["price"] for o in mercado["outcomes"]]
            justas = self._devig(precios)

            for nombre, precio, prob in zip(nombres, precios, justas):
                probs_por_resultado.setdefault(nombre, []).append(prob)
                actual_mejor = mejor_por_resultado.get(nombre)
                if actual_mejor is None or precio > actual_mejor[0]:
                    mejor_por_resultado[nombre] = (precio, bk.get("title", bk.get("key", "?")))

        resultado = {}
        for nombre, probs in probs_por_resultado.items():
            if len(probs) < self.MIN_CASAS:
                continue
            mejor_precio, mejor_casa = mejor_por_resultado[nombre]
            resultado[nombre] = {
                "fair_prob": float(np.mean(probs)),
                "std": float(np.std(probs)),
                "best_price": mejor_precio,
                "best_book": mejor_casa,
                "n_books": len(probs),
            }
        return resultado

    def _consenso_totales(self, bookmakers: list) -> dict:
        """Probabilidad justa de Más/Menos sobre la línea de totales más comparada."""
        por_linea = {}

        for bk in bookmakers:
            mercado = next((m for m in bk.get("markets", []) if m["key"] == "totals"), None)
            if not mercado:
                continue

            precios_por_punto = {}
            for o in mercado.get("outcomes", []):
                precios_por_punto.setdefault(o["point"], {})[o["name"]] = o["price"]

            for punto, lados in precios_por_punto.items():
                if "Over" not in lados or "Under" not in lados:
                    continue
                precios = [lados["Over"], lados["Under"]]
                justas = self._devig(precios)
                bucket = por_linea.setdefault(punto, {"Over": [], "Under": []})
                bucket["Over"].append((justas[0], lados["Over"], bk.get("title", "?")))
                bucket["Under"].append((justas[1], lados["Under"], bk.get("title", "?")))

        if not por_linea:
            return {}

        # Usamos la línea con más casas comparando (la más representativa del mercado)
        mejor_linea = max(por_linea.keys(), key=lambda p: len(por_linea[p]["Over"]))
        lados = por_linea[mejor_linea]

        resultado = {}
        for lado_nombre, entradas in lados.items():
            if len(entradas) < self.MIN_CASAS:
                continue
            probs = [e[0] for e in entradas]
            precios = [e[1] for e in entradas]
            casas = [e[2] for e in entradas]
            idx_mejor = int(np.argmax(precios))
            resultado[lado_nombre] = {
                "point": mejor_linea,
                "fair_prob": float(np.mean(probs)),
                "std": float(np.std(probs)),
                "best_price": precios[idx_mejor],
                "best_book": casas[idx_mejor],
                "n_books": len(entradas),
            }
        return resultado

    def _consenso_handicap(self, bookmakers: list) -> list:
        """Probabilidad justa de cada lado del hándicap (spread) más comparado."""
        por_linea = {}

        for bk in bookmakers:
            mercado = next((m for m in bk.get("markets", []) if m["key"] == "spreads"), None)
            if not mercado or len(mercado.get("outcomes", [])) != 2:
                continue

            o1, o2 = mercado["outcomes"]
            clave = (round(o1["point"], 1), round(o2["point"], 1))
            precios = [o1["price"], o2["price"]]
            justas = self._devig(precios)

            bucket = por_linea.setdefault(clave, {"nombres": (o1["name"], o2["name"]), "datos": ([], [])})
            bucket["datos"][0].append((justas[0], o1["price"], bk.get("title", "?")))
            bucket["datos"][1].append((justas[1], o2["price"], bk.get("title", "?")))

        if not por_linea:
            return []

        mejor_clave = max(por_linea.keys(), key=lambda k: len(por_linea[k]["datos"][0]))
        bucket = por_linea[mejor_clave]

        resultados = []
        for idx in range(2):
            entradas = bucket["datos"][idx]
            if len(entradas) < self.MIN_CASAS:
                continue
            probs = [e[0] for e in entradas]
            precios = [e[1] for e in entradas]
            casas = [e[2] for e in entradas]
            idx_mejor = int(np.argmax(precios))
            resultados.append({
                "equipo": bucket["nombres"][idx],
                "point": mejor_clave[idx],
                "fair_prob": float(np.mean(probs)),
                "std": float(np.std(probs)),
                "best_price": precios[idx_mejor],
                "best_book": casas[idx_mejor],
                "n_books": len(entradas),
            })
        return resultados

    def analizar_partidos(self, partidos_api: list, deporte: str) -> list:
        filas = []

        for item in partidos_api:
            local = item.get("home_team", "Local")
            visitante = item.get("away_team", "Visitante")
            bookmakers = item.get("bookmakers", [])
            if not bookmakers:
                continue

            partido_label = f"{local} vs {visitante}"

            # --- Ganador del partido ---
            for nombre_resultado, datos in self._consenso_h2h(bookmakers).items():
                ev = (datos["fair_prob"] * datos["best_price"]) - 1
                filas.append({
                    "Deporte": deporte,
                    "Partido": partido_label,
                    "Mercado": f"Ganador: {nombre_resultado}",
                    "Prob. Justa (mercado)": f"{datos['fair_prob'] * 100:.1f}%",
                    "Mejor Cuota": datos["best_price"],
                    "Casa": datos["best_book"],
                    "Valor Esperado (EV)": round(ev, 3),
                    "Casas Comparadas": datos["n_books"],
                    "Acuerdo entre Casas": self._nivel_acuerdo(datos["std"]),
                    "es_value_bet": ev > 0,
                })

            # --- Totales (más/menos) ---
            for lado, datos in self._consenso_totales(bookmakers).items():
                etiqueta = "Más de" if lado == "Over" else "Menos de"
                ev = (datos["fair_prob"] * datos["best_price"]) - 1
                filas.append({
                    "Deporte": deporte,
                    "Partido": partido_label,
                    "Mercado": f"{etiqueta} {datos['point']} (Total)",
                    "Prob. Justa (mercado)": f"{datos['fair_prob'] * 100:.1f}%",
                    "Mejor Cuota": datos["best_price"],
                    "Casa": datos["best_book"],
                    "Valor Esperado (EV)": round(ev, 3),
                    "Casas Comparadas": datos["n_books"],
                    "Acuerdo entre Casas": self._nivel_acuerdo(datos["std"]),
                    "es_value_bet": ev > 0,
                })

            # --- Hándicap ---
            for datos in self._consenso_handicap(bookmakers):
                ev = (datos["fair_prob"] * datos["best_price"]) - 1
                filas.append({
                    "Deporte": deporte,
                    "Partido": partido_label,
                    "Mercado": f"Hándicap: {datos['equipo']} {datos['point']:+}",
                    "Prob. Justa (mercado)": f"{datos['fair_prob'] * 100:.1f}%",
                    "Mejor Cuota": datos["best_price"],
                    "Casa": datos["best_book"],
                    "Valor Esperado (EV)": round(ev, 3),
                    "Casas Comparadas": datos["n_books"],
                    "Acuerdo entre Casas": self._nivel_acuerdo(datos["std"]),
                    "es_value_bet": ev > 0,
                })

        return filas


# -----------------------------------------------------------------------------
# MÓDULO 3: INTERFAZ DE USUARIO
# -----------------------------------------------------------------------------
def main():
    st.title("🍊 BETANALYTICS PRO")
    st.subheader("Consenso de Mercado: Probabilidad Justa y Valor Esperado real")
    st.markdown("---")

    st.sidebar.header("🔑 CONEXIÓN EN TIEMPO REAL")
    user_api_key = st.sidebar.text_input(
        label="Ingresa tu The Odds API Key:",
        type="password",
    )

    st.sidebar.markdown("---")
    st.sidebar.header("🏆 FILTROS")
    min_casas = st.sidebar.slider(
        "Mínimo de casas de apuestas comparadas", min_value=2, max_value=8, value=3,
        help="Más casas comparadas = consenso de mercado más confiable.",
    )
    solo_value_bets = st.sidebar.checkbox("Mostrar solo Value Bets (EV > 0)", value=False)

    st.sidebar.markdown("---")
    st.sidebar.header("⚽ DEPORTES")
    deporte_activo = st.sidebar.radio(
        "Selecciona un deporte para analizar:",
        options=[
            "⚽ Fútbol (Mundial)",
            "🏀 Básquetbol (NBA)",
            "⚾ Béisbol (MLB)",
            "🏈 Fútbol Americano (NFL)",
        ],
    )

    with st.expander("ℹ️ ¿Cómo se calculan estos números?"):
        st.markdown(
            "Para cada partido se toman las cuotas de varias casas de apuestas y se les quita "
            "el margen propio de cada casa (el 'vig'), obteniendo así una probabilidad justa de "
            "mercado para cada resultado. El Valor Esperado (EV) compara esa probabilidad justa "
            "contra la mejor cuota disponible: si EV > 0, esa cuota paga más de lo que el mercado "
            "considera justo. Esto no es una predicción ni garantiza ganar una apuesta puntual: "
            "es una métrica estadística de largo plazo. Apostar implica riesgo real de pérdida de "
            "dinero; juega con responsabilidad."
        )

    fetcher = SportDataFetcher(user_api_key)
    engine = BetAnalyticsEngine()

    with st.spinner("Consultando cuotas en vivo..."):
        datos_api, error = fetcher.fetch_live_data(deporte_activo)

    if error:
        st.warning(f"⚠️ {error}")
        st.stop()

    analisis_completo = engine.analizar_partidos(datos_api, deporte_activo)

    if not analisis_completo:
        st.info(
            "No hay suficientes casas de apuestas comparables todavía para calcular un consenso "
            "confiable en estos partidos. Intenta más tarde o reduce el mínimo de casas comparadas."
        )
        st.stop()

    df = pd.DataFrame(analisis_completo)

    if solo_value_bets:
        df = df[df["es_value_bet"] == True]
    df = df[df["Casas Comparadas"] >= min_casas]

    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric(label="🏟️ Partidos Hoy", value=len(datos_api))
    with col2:
        st.metric(label="📊 Mercados Analizados", value=len(df))
    with col3:
        val_count = int(df["es_value_bet"].sum()) if not df.empty else 0
        st.metric(label="💥 Value Bets Encontradas", value=val_count)
    with col4:
        prom_ev = df["Valor Esperado (EV)"].mean() if not df.empty else 0
        st.metric(label="🎯 EV Promedio", value=f"{prom_ev:+.3f}")

    st.markdown("---")
    st.markdown("### 📊 Matriz de Oportunidades (consenso real de mercado)")

    columnas_mostrar = [
        "Partido", "Mercado", "Prob. Justa (mercado)", "Mejor Cuota", "Casa",
        "Valor Esperado (EV)", "Casas Comparadas", "Acuerdo entre Casas",
    ]

    if not df.empty:
        df_mostrar = df[columnas_mostrar]
        st.dataframe(
            df_mostrar.style.background_gradient(subset=["Valor Esperado (EV)"], cmap="RdYlGn"),
            use_container_width=True,
            height=500,
        )
    else:
        st.info("No hay jugadas que coincidan con los filtros seleccionados.")

    st.markdown("---")
    st.caption(
        "BetAnalytics Pro no es asesoría financiera ni garantiza resultados. El EV positivo es una "
        "medida estadística de largo plazo, no una predicción de un resultado individual. Apostar "
        "conlleva riesgo de pérdida de dinero."
    )


if __name__ == "__main__":
    main()
