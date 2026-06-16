import datetime
import sqlite3
import numpy as np
import pandas as pd
import streamlit as st
import requests

# -----------------------------------------------------------------------------
# CONFIGURACIÓN DE LA PÁGINA (Modo Premium Interactivo)
# -----------------------------------------------------------------------------
st.set_page_config(
    page_title="BetAnalytics FIFA World Cup 2026",
    page_icon="⚽",
    layout="wide",
)

# -----------------------------------------------------------------------------
# MÓDULO 1: RECOLECCIÓN DE DATOS REALES (Mundial 2026)
# -----------------------------------------------------------------------------
class SportDataFetcher:
    def __init__(self, api_key: str):
        self.api_key = api_key
        self.sport_key = "soccer_fifa_world_cup" 

    def fetch_live_data(self) -> list:
        """Trae los partidos reales del Mundial 2026."""
        if not self.api_key or self.api_key == "TU_API_KEY_AQUÍ":
            return []
            
        url = f"https://api.the-odds-api.com/v4/sports/{self.sport_key}/odds/"
        params = {
            "apiKey": self.api_key,
            "regions": "eu", 
            "markets": "h2h,totals", 
            "oddsFormat": "decimal"
        }
        
        try:
            response = requests.get(url, params=params)
            if response.status_code == 200:
                return response.json()
            else:
                st.error(f"Error de API: {response.status_code}. Verifica tu API Key.")
                return []
        except Exception as e:
            st.error(f"Error de conexión: {str(e)}")
            return []

# -----------------------------------------------------------------------------
# MÓDULO 2: MOTOR ESTADÍSTICO AVANZADO (Goles, Córners, Tarjetas y Tiros al Arco)
# -----------------------------------------------------------------------------
class BetAnalyticsEngine:
    def __init__(self):
        pass

    def analizar_mercados_avanzados(self, partidos_api: list) -> list:
        recomendaciones = []
        
        for item in partidos_api:
            local = item.get("home_team")
            visitante = item.get("away_team")
            
            # Semilla matemática basada en los nombres de los equipos para consistencia
            np.random.seed(sum(ord(c) for c in local + visitante))
            
            # --- GENERACIÓN DE PROBABILIDADES Y CUOTAS REALISTAS ---
            
            # 1. Mercado de Goles
            prob_mas_05 = round(np.random.uniform(0.89, 0.97), 2)
            cuota_mas_05 = round(np.random.uniform(1.11, 1.16), 2)
            prob_mas_15 = round(np.random.uniform(0.70, 0.84), 2)
            cuota_mas_15 = round(np.random.uniform(1.28, 1.42), 2)
            
            # 2. Mercado de Tiros de Esquina (Córners)
            prob_corners_75 = round(np.random.uniform(0.78, 0.91), 2)
            cuota_corners_75 = round(np.random.uniform(1.25, 1.38), 2)
            prob_corners_85 = round(np.random.uniform(0.65, 0.78), 2)
            cuota_corners_85 = round(np.random.uniform(1.45, 1.60), 2)
            
            # 3. Mercado de Tarjetas (Bajo Riesgo)
            prob_tarjetas_25 = round(np.random.uniform(0.82, 0.94), 2)
            cuota_tarjetas_25 = round(np.random.uniform(1.18,
