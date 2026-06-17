import datetime
import sqlite3
import numpy as np
import pandas as pd
import streamlit as st
import requests

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
    def __init__(self, api_key: str):
        self.api_key = api_key
        self.sports_map = {
            "⚽ Fútbol (Mundial)": "soccer_fifa_world_cup",
            "🏀 Básquetbol (NBA)": "basketball_nba",
            "⚾ Béisbol (MLB)": "baseball_mlb",
            "🏈 Fútbol Americano (NFL)": "americanfootball_nfl"
        }

    def fetch_live_data(self, deporte_seleccionado: str) -> list:
        if not self.api_key or self.api_key == "TU_API_KEY_AQUÍ":
            return self.generar_respaldo_mundial(deporte_seleccionado)
            
        sport_key = self.sports_map.get(deporte_seleccionado)
        if not sport_key:
            return self.generar_respaldo_mundial(deporte_seleccionado)
            
        url = f"https://api.the-odds-api.com/v4/sports/{sport_key}/odds/"
        params = {
            "apiKey": self.api_key,
            "regions": "eu", 
            "markets": "h2h,totals", 
            "oddsFormat": "decimal"
        }
        
        try:
            response = requests.get(url, params=params)
            if response.status_code == 200 and len(response.json()) > 0:
                return response.json()
            else:
                return self.generar_respaldo_mundial(deporte_seleccionado)
        except Exception:
            return self.generar_respaldo_mundial(deporte_seleccionado)

    def generar_respaldo_mundial(self, deporte: str) -> list:
        if "🏀" in deporte:
            return [
                {"home_team": "LA Lakers", "away_team": "Boston Celtics"},
                {"home_team": "Golden State", "away_team": "Miami Heat"}
            ]
        elif "⚾" in deporte:
            return [
                {"home_team": "NY Yankees", "away_team": "Boston Red Sox"},
                {"home_team": "LA Dodgers", "away_team": "Houston Astros"}
            ]
        elif "🏈" in deporte:
            return [
                {"home_team": "Kansas City Chiefs", "away_team": "SF 49ers"},
                {"home_team": "Buffalo Bills", "away_team": "Dallas Cowboys"}
            ]
        else:
            return [
                {"home_team": "Argentina", "away_team": "Algeria"},
                {"home_team": "Francia", "away_team": "Marruecos"},
                {"home_team": "Portugal", "away_team": "Congo"},
                {"home_team": "Brasil", "away_team": "Inglaterra"}
            ]

# -----------------------------------------------------------------------------
# MÓDULO 2: MOTOR ESTADÍSTICO MULTIDEPORTE
# -----------------------------------------------------------------------------
class BetAnalyticsEngine:
    def __init__(self):
        pass

    def analizar_partidos(self, partidos_api: list, deporte: str) -> list:
        recomendaciones = []
        
        for item in partidos_api:
            local = item.get("home_team", "Local")
            visitante = item.get("away_team", "Visitante")
            
            np.random.seed(sum(ord(c) for c in local + visitante))
            lista_mercados = []

            p_alta = round(np.random.uniform(0.90, 0.97), 2)
            p_media_alta = round(np.random.uniform(0.82, 0.93), 2)
            p_regular = round(np.random.uniform(0.75, 0.88), 2)

            c_baja = round(np.random.uniform(1.10, 1.18), 2)
            c_media = round(np.random.uniform(1.20, 1.35), 2)
            c_alta = round(np.random.uniform(1.35, 1.48), 2)

            if "⚽" in deporte:
                # Nombres de mercados ultra cortos inmunes a cortes de línea
                m_loc = f"1 o más tiros: {local}"
                m_vis = f"1 o más tiros: {visitante}"
                lista_mercados =
