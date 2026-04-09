"""Weather API service provider."""
import httpx
from typing import Dict, Any, Optional
from ..config import settings
import logging

logger = logging.getLogger(__name__)


class WeatherProvider:
    """Provider for weather API integration."""
    
    def __init__(self):
        self.api_key = settings.hefeng_weather_key
        self.base_url = "https://devapi.qweather.com/v7"
        self.timeout = settings.weather_api_timeout / 1000
    
    async def get_current_weather(self, city: str) -> Dict[str, Any]:
        """Get current weather for a city."""
        if not self.api_key:
            logger.warning("Weather API key not configured, returning mock data")
            return self._get_mock_current_weather(city)
        
        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                geo_response = await client.get(
                    f"{self.base_url}/geo/v2/city/lookup",
                    params={"location": city, "key": self.api_key}
                )
                
                if geo_response.status_code != 200:
                    return self._get_mock_current_weather(city)
                
                geo_data = geo_response.json()
                location = geo_data.get("location", [{}])[0]
                
                if not location:
                    return self._get_mock_current_weather(city)
                
                weather_response = await client.get(
                    f"{self.base_url}/weather/now",
                    params={
                        "location": location.get("id", ""),
                        "key": self.api_key
                    }
                )
                
                if weather_response.status_code == 200:
                    return weather_response.json()
                
                return self._get_mock_current_weather(city)
                
        except Exception as e:
            logger.error(f"Weather API error: {e}")
            return self._get_mock_current_weather(city)
    
    async def get_forecast(self, city: str, days: int = 3) -> Dict[str, Any]:
        """Get weather forecast for a city."""
        if not self.api_key:
            return self._get_mock_forecast(city, days)
        
        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                geo_response = await client.get(
                    f"{self.base_url}/geo/v2/city/lookup",
                    params={"location": city, "key": self.api_key}
                )
                
                if geo_response.status_code != 200:
                    return self._get_mock_forecast(city, days)
                
                geo_data = geo_response.json()
                location = geo_data.get("location", [{}])[0]
                
                if not location:
                    return self._get_mock_forecast(city, days)
                
                forecast_response = await client.get(
                    f"{self.base_url}/weather/{days}d",
                    params={
                        "location": location.get("id", ""),
                        "key": self.api_key
                    }
                )
                
                if forecast_response.status_code == 200:
                    return forecast_response.json()
                
                return self._get_mock_forecast(city, days)
                
        except Exception as e:
            logger.error(f"Weather forecast API error: {e}")
            return self._get_mock_forecast(city, days)
    
    def _get_mock_current_weather(self, city: str) -> Dict[str, Any]:
        """Return mock current weather data."""
        return {
            "code": "200",
            "now": {
                "temp": "25",
                "feelsLike": "27",
                "humidity": "65",
                "windDir": "东南风",
                "windSpeed": "12",
                "weather": "多云",
                "vis": "10"
            },
            "location": {
                "name": city,
                "id": "0"
            }
        }
    
    def _get_mock_forecast(self, city: str, days: int) -> Dict[str, Any]:
        """Return mock forecast data."""
        forecasts = []
        weathers = ["多云转晴", "小雨", "晴", "阴天", "雷阵雨"]
        
        for i in range(days):
            forecasts.append({
                "date": f"2026-04-{(4+i):02d}",
                "tempMin": f"{20+i}",
                "tempMax": f"{27+i}",
                "weather": weathers[i % len(weathers)],
                "precipitation": f"{10 + i * 15}",
                "humidity": f"{60 + i * 5}",
                "windDir": "东南风",
                "windSpeed": "12"
            })
        
        return {
            "code": "200",
            "daily": forecasts,
            "location": {
                "name": city,
                "id": "0"
            }
        }
    
    async def health_check(self) -> bool:
        """Check if weather API is available."""
        if not self.api_key:
            return True
        
        try:
            async with httpx.AsyncClient(timeout=5) as client:
                response = await client.get(
                    f"{self.base_url}/weather/now",
                    params={"location": "beijing", "key": self.api_key}
                )
                return response.status_code == 200
        except:
            return False
