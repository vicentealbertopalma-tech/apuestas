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
# MÓDULO 1: RECOLECCIÓN DE DATOS
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
# MÓDULO 2: MOTOR ESTADÍSTICO ANTI-FALLOS
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

            p
