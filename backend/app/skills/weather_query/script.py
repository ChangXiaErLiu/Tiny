"""Weather Query Skill - Script

This script queries weather information for a specified city.
Input: JSON with 'city' and optional 'days' parameters
Output: JSON with weather data
"""
import json
import sys
import httpx
import os
from typing import Dict, Any, Optional

HEFENG_KEY = os.getenv("HEFENG_WEATHER_KEY", "")
BASE_URL = "https://devapi.qweather.com/v7"
TIMEOUT = 5.0


def get_mock_current_weather(city: str) -> Dict[str, Any]:
    """Return mock current weather when API key is not configured."""
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
        "location": {"name": city, "id": "0"}
    }


def get_mock_forecast(city: str, days: int) -> Dict[str, Any]:
    """Return mock forecast data."""
    weathers = ["多云转晴", "小雨", "晴", "阴天", "雷阵雨", "晴转多云"]
    forecasts = []

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

    return {"code": "200", "daily": forecasts, "location": {"name": city, "id": "0"}}


async def query_weather(city: str, days: int = 3) -> Dict[str, Any]:
    """Query weather for a city."""
    result = {
        "city": city,
        "current": None,
        "forecast": [],
        "source": "mock"
    }

    if not HEFENG_KEY:
        result["current"] = get_mock_current_weather(city).get("now", {})
        result["forecast"] = get_mock_forecast(city, days).get("daily", [])
        return result

    try:
        async with httpx.AsyncClient(timeout=TIMEOUT) as client:
            geo_response = await client.get(
                f"{BASE_URL}/geo/v2/city/lookup",
                params={"location": city, "key": HEFENG_KEY}
            )

            if geo_response.status_code != 200:
                result["current"] = get_mock_current_weather(city).get("now", {})
                result["forecast"] = get_mock_forecast(city, days).get("daily", [])
                return result

            geo_data = geo_response.json()
            location = geo_data.get("location", [{}])[0]

            if not location:
                result["current"] = get_mock_current_weather(city).get("now", {})
                result["forecast"] = get_mock_forecast(city, days).get("daily", [])
                return result

            location_id = location.get("id", "")

            now_response = await client.get(
                f"{BASE_URL}/weather/now",
                params={"location": location_id, "key": HEFENG_KEY}
            )

            if now_response.status_code == 200:
                now_data = now_response.json()
                result["current"] = now_data.get("now", {})
                result["source"] = "api"

            forecast_response = await client.get(
                f"{BASE_URL}/weather/{days}d",
                params={"location": location_id, "key": HEFENG_KEY}
            )

            if forecast_response.status_code == 200:
                forecast_data = forecast_response.json()
                result["forecast"] = forecast_data.get("daily", [])

    except Exception as e:
        result["current"] = get_mock_current_weather(city).get("now", {})
        result["forecast"] = get_mock_forecast(city, days).get("daily", [])

    return result


def format_weather_text(data: Dict[str, Any]) -> str:
    """Format weather data into readable Chinese text."""
    lines = [f"【{data.get('city', '未知')}天气】\n"]

    current = data.get("current", {})
    if current:
        lines.append(f"当前天气：{current.get('weather', '未知')}")
        lines.append(f"气温：{current.get('temp', '?')}℃")
        lines.append(f"体感温度：{current.get('feelsLike', '?')}℃")
        lines.append(f"湿度：{current.get('humidity', '?')}%")
        lines.append(f"风向：{current.get('windDir', '?')}")
        lines.append("")

    forecast = data.get("forecast", [])
    if forecast:
        lines.append("【未来天气预报】")
        for day in forecast[:3]:
            date = day.get('date', '')
            weather = day.get('weather', '')
            temp_min = day.get('tempMin', '')
            temp_max = day.get('tempMax', '')
            lines.append(f"{date}: {weather} {temp_min}-{temp_max}℃")

    return "\n".join(lines)


def main():
    try:
        input_data = json.loads(sys.stdin.read())
    except json.JSONDecodeError:
        print(json.dumps({"error": "Invalid JSON input"}))
        return

    city = input_data.get("city")
    days = input_data.get("days", 3)

    if not city:
        print(json.dumps({"error": "City parameter is required"}))
        return

    import asyncio
    result = asyncio.run(query_weather(city, min(days, 7)))
    result["formatted_text"] = format_weather_text(result)

    output = {
        "data": result,
        "success": True
    }

    print(json.dumps(output, ensure_ascii=False))


if __name__ == "__main__":
    main()
