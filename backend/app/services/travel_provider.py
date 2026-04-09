"""Travel information provider."""
import httpx
from typing import Dict, Any, List, Optional
from ..config import settings
import logging

logger = logging.getLogger(__name__)


class TravelProvider:
    """Provider for travel/POI information."""
    
    def __init__(self):
        self.amap_key = settings.amap_key
        self.amap_secret = settings.amap_secret
        self.base_url = "https://restapi.amap.com/v3"
        self.timeout = settings.travel_api_timeout / 1000
    
    async def search_attractions(self, city: str, keywords: str = "景点") -> List[Dict[str, Any]]:
        """Search for attractions in a city."""
        if not self.amap_key:
            return self._get_mock_attractions(city)
        
        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.get(
                    f"{self.base_url}/place/text",
                    params={
                        "key": self.amap_key,
                        "keywords": keywords,
                        "city": city,
                        "offset": 0,
                        "limit": 10,
                        "types": "风景名胜"
                    }
                )
                
                if response.status_code == 200:
                    data = response.json()
                    if data.get("status") == "1":
                        pois = data.get("pois", [])
                        return [self._parse_poi(p) for p in pois]
                
                return self._get_mock_attractions(city)
                
        except Exception as e:
            logger.error(f"Travel API error: {e}")
            return self._get_mock_attractions(city)
    
    async def get_attraction_details(self, poi_id: str) -> Optional[Dict[str, Any]]:
        """Get details for a specific attraction."""
        if not self.amap_key:
            return None
        
        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.get(
                    f"{self.base_url}/place/detail",
                    params={
                        "key": self.amap_key,
                        "id": poi_id
                    }
                )
                
                if response.status_code == 200:
                    data = response.json()
                    if data.get("status") == "1":
                        return self._parse_poi(data.get("pois", [{}])[0])
                
                return None
                
        except Exception as e:
            logger.error(f"Travel detail API error: {e}")
            return None
    
    def _parse_poi(self, poi: Dict[str, Any]) -> Dict[str, Any]:
        """Parse POI data into standard format."""
        return {
            "id": poi.get("id", ""),
            "name": poi.get("name", ""),
            "address": poi.get("address", ""),
            "location": poi.get("location", ""),
            "type": poi.get("type", ""),
            "tel": poi.get("tel", ""),
            "rating": poi.get("rating", ""),
            "business_hours": poi.get("businesshours", ""),
            "description": poi.get("description", ""),
            "photo_urls": poi.get("photos", [{}])[0].get("url", "") if poi.get("photos") else ""
        }
    
    def _get_mock_attractions(self, city: str) -> List[Dict[str, Any]]:
        """Return mock attraction data."""
        base_attractions = {
            "南宁": [
                {"id": "1", "name": "青秀山", "address": "南宁市青秀区凤岭南路", "rating": "4.6", 
                 "type": "风景名胜", "business_hours": "06:00-18:00", 
                 "description": "南宁市最著名的景点，风景优美"},
                {"id": "2", "name": "南湖公园", "address": "南宁市青秀区双拥路", "rating": "4.4",
                 "type": "公园", "business_hours": "全天开放",
                 "description": "市区内的大型公园，适合休闲漫步"},
                {"id": "3", "name": "广西民族博物馆", "address": "南宁市青秀区青环路", "rating": "4.5",
                 "type": "博物馆", "business_hours": "09:00-17:00",
                 "description": "展示广西各民族文化风情"},
                {"id": "4", "name": "大明山", "address": "南宁市武鸣区", "rating": "4.3",
                 "type": "自然保护区", "business_hours": "08:00-17:00",
                 "description": "登山观光，夏季避暑胜地"}
            ],
            "桂林": [
                {"id": "5", "name": "象鼻山", "address": "桂林市象山区", "rating": "4.7",
                 "type": "风景名胜", "business_hours": "06:30-19:00",
                 "description": "桂林城徽，标志性景点"},
                {"id": "6", "name": "漓江", "address": "桂林市灵川县", "rating": "4.8",
                 "type": "江河", "business_hours": "全天",
                 "description": "山水甲天下，最美河流"},
                {"id": "7", "name": "阳朔西街", "address": "桂林市阳朔县", "rating": "4.5",
                 "type": "商业街", "business_hours": "全天",
                 "description": "千年古街，充满异国风情"}
            ]
        }
        
        return base_attractions.get(city, base_attractions.get("南宁", []))
    
    async def health_check(self) -> bool:
        """Check if travel API is available."""
        if not self.amap_key:
            return True
        
        try:
            async with httpx.AsyncClient(timeout=5) as client:
                response = await client.get(
                    f"{self.base_url}/config/district",
                    params={"key": self.amap_key, "keywords": "中国"}
                )
                return response.status_code == 200
        except:
            return False
