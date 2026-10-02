"""Клиент Open-Meteo: текущая погода + прогноз (без API-ключа)."""
import requests


GEO_URL = "https://geocoding-api.open-meteo.com/v1/search"
FORECAST_URL = "https://api.open-meteo.com/v1/forecast"


class OpenMeteoClient:
    def __init__(self, timeout: int = 10):
        self.timeout = timeout
        self._session = requests.Session()

    def geocode(self, city: str) -> dict | None:
        """Город → {name, country, latitude, longitude}."""
        r = self._session.get(
            GEO_URL,
            params={"name": city, "count": 1, "language": "ru", "format": "json"},
            timeout=self.timeout,
        )
        r.raise_for_status()
        results = r.json().get("results") or []
        if not results:
            return None
        hit = results[0]
        return {
            "name": hit["name"],
            "country": hit.get("country", ""),
            "latitude": hit["latitude"],
            "longitude": hit["longitude"],
        }

    def current(self, lat: float, lon: float) -> dict:
        """Текущая погода."""
        r = self._session.get(
            FORECAST_URL,
            params={
                "latitude": lat,
                "longitude": lon,
                "current": "temperature_2m,relative_humidity_2m,wind_speed_10m,weather_code",
                "timezone": "auto",
            },
            timeout=self.timeout,
        )
        r.raise_for_status()
        cur = r.json()["current"]
        return {
            "temperature": cur["temperature_2m"],
            "humidity": cur["relative_humidity_2m"],
            "wind": cur["wind_speed_10m"],
            "code": cur["weather_code"],
        }

    def forecast(self, lat: float, lon: float, days: int = 5) -> dict:
        """Прогноз: {dates[], temp_max[], temp_min[]}."""
        r = self._session.get(
            FORECAST_URL,
            params={
                "latitude": lat,
                "longitude": lon,
                "daily": "temperature_2m_max,temperature_2m_min",
                "forecast_days": days,
                "timezone": "auto",
            },
            timeout=self.timeout,
        )
        r.raise_for_status()
        daily = r.json()["daily"]
        return {
            "dates": daily["time"],
            "temp_max": daily["temperature_2m_max"],
            "temp_min": daily["temperature_2m_min"],
        }

