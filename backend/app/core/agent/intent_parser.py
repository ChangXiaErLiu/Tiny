"""LLM-based intent parser that understands SKILL.md documents."""
import re
import json
from typing import Dict, Any, List, Optional
from .base import Intent, IntentType
import logging

logger = logging.getLogger(__name__)


class IntentParser:
    """Parses user input using LLM understanding of skill documents."""
    
    def __init__(self, skill_manifests: Dict[str, Dict[str, Any]]):
        self.skill_manifests = skill_manifests
    
    async def parse(self, user_input: str) -> Intent:
        """Parse user input into structured intent using skill knowledge."""
        
        intent = Intent(
            type=IntentType.UNKNOWN,
            confidence=0.0,
            raw_input=user_input
        )
        
        intent.type, intent.confidence = self._rule_based_intent(user_input)
        
        if intent.type == IntentType.UNKNOWN:
            return intent
        
        intent.target_skills = self._get_skills_for_intent(intent.type)
        intent.parameters = self._extract_parameters(user_input, intent.type)
        
        return intent
    
    def _rule_based_intent(self, user_input: str) -> tuple[IntentType, float]:
        """Use simple rules to determine intent type."""
        user_input_lower = user_input.lower()
        
        combined_indicators = [
            (r'天气.*旅游|旅游.*天气', 2),
            (r'游玩.*注意.*天气|带伞.*玩', 2),
            (r'\d+天.*\w+.*计划|去.*\d+天.*旅游', 1),
        ]
        
        combined_score = 0
        for pattern, weight in combined_indicators:
            if re.search(pattern, user_input_lower):
                combined_score += weight
        
        if combined_score >= 2:
            return IntentType.COMBINED, 0.85
        
        weather_indicators = [
            (r'天气|气温|温度|下雨|下雪|晴|冷|热', 1),
            (r'需要带伞|要不要带伞', 1),
            (r'适合出门|出去玩', 1),
        ]
        
        weather_score = sum(weight for pattern, weight in weather_indicators 
                          if re.search(pattern, user_input_lower))
        
        travel_indicators = [
            (r'旅游|旅行|游玩|行程|攻略', 1),
            (r'\d+天.*去|去.*\d+天', 2),
            (r'计划|安排', 1),
        ]
        
        travel_score = sum(weight for pattern, weight in travel_indicators 
                          if re.search(pattern, user_input_lower))
        
        if weather_score >= 2 and travel_score >= 1:
            return IntentType.COMBINED, 0.8
        elif weather_score >= 2:
            return IntentType.WEATHER_QUERY, min(0.5 + weather_score * 0.2, 0.9)
        elif travel_score >= 2:
            return IntentType.TRAVEL_PLAN, min(0.5 + travel_score * 0.2, 0.9)
        elif weather_score >= 1:
            return IntentType.WEATHER_QUERY, 0.5
        elif travel_score >= 1:
            return IntentType.TRAVEL_PLAN, 0.5
        
        return IntentType.UNKNOWN, 0.0
    
    def _get_skills_for_intent(self, intent_type: IntentType) -> List[str]:
        """Map intent type to skill names."""
        mapping = {
            IntentType.WEATHER_QUERY: ["weather_query"],
            IntentType.TRAVEL_PLAN: ["travel_planner"],
            IntentType.COMBINED: ["weather_query", "travel_planner"],
        }
        return mapping.get(intent_type, [])
    
    def _extract_parameters(self, user_input: str, intent_type: IntentType) -> Dict[str, Any]:
        """Extract parameters from user input based on intent."""
        params = {}
        
        cities = [
            "南宁", "桂林", "北海", "柳州", "梧州", "贵港", "玉林",
            "北京", "上海", "广州", "深圳", "杭州", "成都", "重庆",
            "西安", "厦门", "三亚", "青岛", "大连", "武汉"
        ]
        for city in cities:
            if city in user_input:
                params["city"] = city
                break
        
        if "city" not in params:
            city_match = re.search(r'去([^\s\d]+)旅游|去([^\s]+)玩', user_input)
            if city_match:
                params["city"] = city_match.group(1) or city_match.group(2)
        
        days_match = re.search(r'(\d+)天', user_input)
        if days_match:
            params["days"] = int(days_match.group(1))
        elif intent_type == IntentType.TRAVEL_PLAN or intent_type == IntentType.COMBINED:
            params["days"] = 3
        
        date_match = re.search(r'(今天|明天|后天|本周|下周)', user_input)
        if date_match:
            params["date"] = date_match.group(1)
        
        return params
    
    def build_skill_context_prompt(self, skill_name: str) -> str:
        """Build a prompt describing a skill for LLM context."""
        manifest = self.skill_manifests.get(skill_name)
        if not manifest:
            return ""
        
        prompt_parts = [
            f"## Skill: {manifest.get('name', skill_name)}",
            manifest.get('description', ''),
            "",
            "### Use Cases:"
        ]
        
        for use_case in manifest.get('use_cases', []):
            prompt_parts.append(f"- {use_case}")
        
        prompt_parts.extend([
            "",
            "### Parameters:"
        ])
        
        for param_name, param_info in manifest.get('parameters', {}).items():
            required = "Required" if param_info.get('required') else "Optional"
            prompt_parts.append(f"- {param_name} ({required}): {param_info.get('description', '')}")
        
        return "\n".join(prompt_parts)
