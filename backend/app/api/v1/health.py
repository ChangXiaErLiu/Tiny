"""Health check endpoint."""
from fastapi import APIRouter
from ...schemas.response import HealthResponse
from ...services.weather_provider import WeatherProvider
from ...services.travel_provider import TravelProvider
from ...services.llm_provider import LLMProvider
import time

router = APIRouter()


@router.get("/health", response_model=HealthResponse)
async def health_check():
    """Check the health status of the API and its dependencies."""
    services = {}
    overall_healthy = True
    
    providers = [
        ("weather_api", WeatherProvider()),
        ("travel_api", TravelProvider()),
        ("deepseek_api", LLMProvider())
    ]
    
    for name, provider in providers:
        start = time.time()
        try:
            is_healthy = await provider.health_check()
            latency = (time.time() - start) * 1000
            
            if is_healthy:
                services[name] = "connected"
            else:
                services[name] = "degraded"
                overall_healthy = False
        except Exception as e:
            services[name] = f"error: {str(e)}"
            overall_healthy = False
    
    return HealthResponse(
        code=200,
        message="success",
        status="healthy" if overall_healthy else "degraded",
        version="1.0.0",
        services=services
    )
