"""Travel Planner Skill - Script

This script generates travel plans based on city, days, and weather.
Input: JSON with 'city', 'days', optional 'weather_data'
Output: JSON with travel plan
"""
import json
import sys
import httpx
import os
from typing import Dict, Any, List, Optional

AMAP_KEY = os.getenv("AMAP_KEY", "")
BASE_URL = "https://restapi.amap.com/v3"
TIMEOUT = 5.0


MOCK_ATTRACTIONS = {
    "南宁": [
        {"name": "青秀山", "type": "风景名胜", "rating": "4.6", "hours": "06:00-18:00", "desc": "南宁市最著名的景点，风景优美"},
        {"name": "南湖公园", "type": "公园", "rating": "4.4", "hours": "全天", "desc": "市区内的大型公园，适合休闲漫步"},
        {"name": "广西民族博物馆", "type": "博物馆", "rating": "4.5", "hours": "09:00-17:00", "desc": "展示广西各民族文化风情"},
        {"name": "大明山", "type": "自然保护区", "rating": "4.3", "hours": "08:00-17:00", "desc": "登山观光，夏季避暑胜地"}
    ],
    "桂林": [
        {"name": "象鼻山", "type": "风景名胜", "rating": "4.7", "hours": "06:30-19:00", "desc": "桂林城徽，标志性景点"},
        {"name": "漓江", "type": "江河", "rating": "4.8", "hours": "全天", "desc": "山水甲天下，最美河流"},
        {"name": "阳朔西街", "type": "商业街", "rating": "4.5", "hours": "全天", "desc": "千年古街，充满异国风情"},
        {"name": "遇龙河", "type": "江河", "rating": "4.7", "hours": "全天", "desc": "最美骑行路线，风景如画"}
    ],
    "北海": [
        {"name": "银滩", "type": "海滩", "rating": "4.5", "hours": "全天", "desc": "天下第一滩，沙质细腻"},
        {"name": "涠洲岛", "type": "海岛", "rating": "4.8", "hours": "全天", "desc": "中国最大火山岛，景色绝美"},
        {"name": "北海老街", "type": "历史文化", "rating": "4.3", "hours": "全天", "desc": "百年老街，中西合璧建筑"}
    ]
}


async def search_attractions(city: str) -> List[Dict[str, Any]]:
    """Search for attractions in a city."""
    if not AMAP_KEY:
        return MOCK_ATTRACTIONS.get(city, MOCK_ATTRACTIONS.get("南宁", []))

    try:
        async with httpx.AsyncClient(timeout=TIMEOUT) as client:
            response = await client.get(
                f"{BASE_URL}/place/text",
                params={
                    "key": AMAP_KEY,
                    "keywords": "景点,公园,博物馆",
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
                    return [
                        {
                            "name": p.get("name", ""),
                            "type": p.get("type", ""),
                            "rating": p.get("rating", ""),
                            "hours": p.get("businesshours", "全天"),
                            "desc": p.get("address", "")
                        }
                        for p in pois[:8]
                    ]
    except Exception:
        pass

    return MOCK_ATTRACTIONS.get(city, MOCK_ATTRACTIONS.get("南宁", []))


def generate_travel_plan(
    city: str,
    days: int,
    weather_data: Optional[Dict[str, Any]] = None
) -> Dict[str, Any]:
    """Generate a travel plan for the city."""
    plan = {
        "city": city,
        "days": days,
        "daily_plans": [],
        "tips": []
    }

    attractions = MOCK_ATTRACTIONS.get(city, MOCK_ATTRACTIONS.get("南宁", []))

    weather_forecast = []
    if weather_data and weather_data.get("forecast"):
        weather_forecast = weather_data.get("forecast", [])[:days]

    for day in range(1, days + 1):
        day_plan = {
            "day": day,
            "date": f"第{day}天",
            "morning": None,
            "lunch": None,
            "afternoon": None,
            "dinner": None,
            "evening": None,
            "weather": None,
            "tips": []
        }

        if day - 1 < len(weather_forecast):
            day_weather = weather_forecast[day - 1]
            day_plan["weather"] = day_weather.get("weather", "")

            if "雨" in day_weather.get("weather", ""):
                day_plan["tips"].append("今天有雨，记得带伞！建议安排室内活动")

        spot_idx = (day - 1) % len(attractions)
        morning_spot = attractions[spot_idx]

        if "雨" not in (day_plan["weather"] or ""):
            day_plan["morning"] = {
                "activity": f"游览【{morning_spot['name']}】",
                "duration": "3小时",
                "tips": morning_spot.get("desc", "")
            }
            day_plan["tips"].append(f"门票：建议提前预订 | 营业时间：{morning_spot.get('hours', '')}")
        else:
            day_plan["morning"] = {
                "activity": "室内活动（根据天气调整）",
                "duration": "3小时",
                "tips": "可考虑博物馆、商场等室内场所"
            }

        lunch_options = ["当地特色餐厅", "小吃街", "美食广场"]
        day_plan["lunch"] = lunch_options[day % len(lunch_options)]

        afternoon_idx = (day) % len(attractions)
        afternoon_spot = attractions[afternoon_idx]

        if "雨" not in (day_plan["weather"] or ""):
            day_plan["afternoon"] = {
                "activity": f"游览【{afternoon_spot['name']}】",
                "duration": "4小时",
                "tips": afternoon_spot.get("desc", "")
            }
        else:
            day_plan["afternoon"] = {
                "activity": "室内休闲活动",
                "duration": "4小时",
                "tips": "可选择SPA、茶馆或电影院"
            }

        dinner_options = ["海鲜餐厅", "夜市小吃", "特色农家乐"]
        day_plan["dinner"] = dinner_options[day % len(dinner_options)]

        if day == days:
            day_plan["evening"] = {
                "activity": "自由活动 / 整理行李",
                "duration": "2小时",
                "tips": "为明天返程做准备"
            }

        plan["daily_plans"].append(day_plan)

    base_tips = [
        f"提前关注当地天气预报，根据天气调整行程",
        "必备物品：身份证、手机、充电宝、常用药品",
        "提前预订酒店和热门景点门票",
        "品尝当地特色美食是旅游的一大乐趣"
    ]
    plan["tips"] = base_tips

    return plan


def format_plan_text(plan: Dict[str, Any]) -> str:
    """Format travel plan into readable text."""
    lines = [
        f"【{plan.get('city', '未知')} {plan.get('days', 0)}日游行程】",
        ""
    ]

    for day_plan in plan.get("daily_plans", []):
        lines.append(f"══ {day_plan.get('date')} ══")

        weather = day_plan.get("weather")
        if weather:
            lines.append(f"天气预报：{weather}")

        morning = day_plan.get("morning")
        if morning:
            lines.append(f"☀ 上午：{morning.get('activity', '')}")
            lines.append(f"   {morning.get('tips', '')}")

        lunch = day_plan.get("lunch")
        if lunch:
            lines.append(f"🍜 午餐：{lunch}")

        afternoon = day_plan.get("afternoon")
        if afternoon:
            lines.append(f"🌤️ 下午：{afternoon.get('activity', '')}")
            lines.append(f"   {afternoon.get('tips', '')}")

        dinner = day_plan.get("dinner")
        if dinner:
            lines.append(f"🍜 晚餐：{dinner}")

        evening = day_plan.get("evening")
        if evening:
            lines.append(f"🌙 晚上：{evening.get('activity', '')}")

        tips = day_plan.get("tips", [])
        if tips:
            lines.append("   📝 提示：" + " | ".join(tips))

        lines.append("")

    lines.append("【总体贴士】")
    for tip in plan.get("tips", []):
        lines.append(f"• {tip}")

    return "\n".join(lines)


async def main_logic(city: str, days: int, weather_data: Optional[Dict] = None) -> Dict[str, Any]:
    """Main logic for generating travel plan."""
    attractions = await search_attractions(city)

    plan = generate_travel_plan(city, days, weather_data)

    if not weather_data:
        plan["attractions"] = attractions[:5]

    plan["formatted_text"] = format_plan_text(plan)

    return plan


def main():
    try:
        input_data = json.loads(sys.stdin.read())
    except json.JSONDecodeError:
        print(json.dumps({"error": "Invalid JSON input"}))
        return

    city = input_data.get("city")
    days = input_data.get("days", 3)
    weather_data = input_data.get("weather_data")

    if not city:
        print(json.dumps({"error": "City parameter is required"}))
        return

    import asyncio
    result = asyncio.run(main_logic(city, days, weather_data))

    output = {
        "data": result,
        "success": True
    }

    print(json.dumps(output, ensure_ascii=False))


if __name__ == "__main__":
    main()
