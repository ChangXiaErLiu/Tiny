"""Chat streaming endpoint for declarative skill framework."""
from fastapi import APIRouter, Request
from fastapi.responses import StreamingResponse
import asyncio
import json
import time
import uuid
import logging

from ...core.agent.intent_parser import IntentParser
from ...core.agent.skill_dispatcher import SkillDispatcher
from ...schemas.request import ChatRequest
from ...core.skill.registry import SkillRegistry
from ...core.agent.base import IntentType
from ...core.tracing import RequestTracer, log_step

router = APIRouter()
logger = logging.getLogger(__name__)


def get_intent_parser() -> IntentParser:
    """Get intent parser with skill manifests."""
    registry = SkillRegistry()
    manifests = registry.list_all()

    skill_manifests = {
        m.name: m.to_dict() for m in manifests
    }

    return IntentParser(skill_manifests)


def get_skill_dispatcher() -> SkillDispatcher:
    """Get skill dispatcher."""
    return SkillDispatcher(SkillRegistry())


async def generate_stream(user_input: str, session_id: str = None):
    """Generate SSE stream for chat response."""
    if not session_id:
        session_id = str(uuid.uuid4())

    with RequestTracer(request_id=session_id, request_data={'message': user_input}) as tracer:
        tracer.begin_step('session_start', {'session_id': session_id})
        tracer.end_step('session_start')

        yield f"event: session_start\ndata: {json.dumps({'session_id': session_id})}\n\n"

        intent_parser = get_intent_parser()
        dispatcher = get_skill_dispatcher()

        tracer.begin_step('intent_parsing', {'input': user_input})
        intent = await intent_parser.parse(user_input)
        tracer.end_step('intent_parsing', {
            'type': intent.type.value,
            'confidence': intent.confidence,
            'target_skills': intent.target_skills,
            'parameters': intent.parameters
        })

        yield f"event: intent_parsed\ndata: {json.dumps({'type': intent.type.value, 'confidence': intent.confidence, 'target_skills': intent.target_skills, 'parameters': intent.parameters})}\n\n"

        skill_results = {}

        if intent.type == IntentType.WEATHER_QUERY:
            tracer.begin_step('skill_weather_query', {'params': intent.parameters})
            yield f"event: skill_start\ndata: {json.dumps({'skill': 'weather_query', 'status': 'start'})}\n\n"

            log_step("Calling dispatcher.dispatch_single for weather_query", intent.parameters)
            weather_result = await dispatcher.dispatch_single(
                "weather_query",
                intent.parameters
            )
            log_step("weather_query result", {'success': weather_result.success, 'data': weather_result.data})

            skill_results["weather_query"] = weather_result.data

            tracer.end_step('skill_weather_query', {
                'success': weather_result.success,
                'execution_time_ms': weather_result.execution_time_ms,
                'data': weather_result.data
            }, error=None if weather_result.success else weather_result.error)

            yield f"event: skill_end\ndata: {json.dumps({'skill': 'weather_query', 'status': 'end', 'success': weather_result.success, 'execution_time_ms': weather_result.execution_time_ms})}\n\n"

            content = format_weather_response(weather_result.data)

        elif intent.type == IntentType.TRAVEL_PLAN:
            tracer.begin_step('skill_travel_planner', {'params': intent.parameters})
            yield f"event: skill_start\ndata: {json.dumps({'skill': 'travel_planner', 'status': 'start'})}\n\n"

            log_step("Calling dispatcher.dispatch_single for travel_planner", intent.parameters)
            travel_result = await dispatcher.dispatch_single(
                "travel_planner",
                intent.parameters
            )
            log_step("travel_planner result", {'success': travel_result.success, 'data': travel_result.data})

            skill_results["travel_planner"] = travel_result.data

            tracer.end_step('skill_travel_planner', {
                'success': travel_result.success,
                'execution_time_ms': travel_result.execution_time_ms,
                'data': travel_result.data
            }, error=None if travel_result.success else travel_result.error)

            yield f"event: skill_end\ndata: {json.dumps({'skill': 'travel_planner', 'status': 'end', 'success': travel_result.success, 'execution_time_ms': travel_result.execution_time_ms})}\n\n"

            content = format_travel_response(travel_result.data)

        elif intent.type == IntentType.COMBINED:
            tracer.begin_step('skill_weather_query', {'params': intent.parameters})
            yield f"event: skill_start\ndata: {json.dumps({'skill': 'weather_query', 'status': 'start'})}\n\n"
            weather_result = await dispatcher.dispatch_single("weather_query", intent.parameters.copy())
            skill_results["weather_query"] = weather_result.data
            tracer.end_step('skill_weather_query', {'success': weather_result.success, 'data': weather_result.data})
            yield f"event: skill_end\ndata: {json.dumps({'skill': 'weather_query', 'status': 'end', 'success': weather_result.success})}\n\n"

            travel_params = intent.parameters.copy()
            if weather_result.success and weather_result.data:
                travel_params["weather_data"] = weather_result.data

            tracer.begin_step('skill_travel_planner', {'params': travel_params})
            yield f"event: skill_start\ndata: {json.dumps({'skill': 'travel_planner', 'status': 'start'})}\n\n"
            travel_result = await dispatcher.dispatch_single("travel_planner", travel_params)
            skill_results["travel_planner"] = travel_result.data
            tracer.end_step('skill_travel_planner', {'success': travel_result.success, 'data': travel_result.data})
            yield f"event: skill_end\ndata: {json.dumps({'skill': 'travel_planner', 'status': 'end', 'success': travel_result.success})}\n\n"

            weather_text = format_weather_response(weather_result.data)
            travel_text = format_travel_response(travel_result.data)
            content = f"{weather_text}\n\n{travel_text}"

        else:
            content = f"您好！收到您的消息：{user_input}。我可以帮您查询天气（输入如：南宁明天天气怎么样）或制定旅游计划（输入如：帮我制定一个三天的南宁旅游计划）。请问有什么可以帮助您的？"

        tracer.begin_step('generate_response', {'content_length': len(content)})
        for char in content:
            yield f"event: content\ndata: {json.dumps({'content': char})}\n\n"
            await asyncio.sleep(0.01)
        tracer.end_step('generate_response', {'content': content})

        tracer.set_result({
            'skill_results': skill_results,
            'usage': {'prompt_tokens': len(user_input), 'completion_tokens': len(content)}
        })

        yield f"event: done\ndata: {json.dumps({'session_id': session_id, 'skill_results': skill_results, 'usage': {'prompt_tokens': len(user_input), 'completion_tokens': len(content), 'total_tokens': len(user_input) + len(content)}})}\n\n"


def format_weather_response(data) -> str:
    """Format weather data into readable text."""
    if not data:
        return "抱歉，无法获取天气信息"

    if isinstance(data, dict):
        return data.get("formatted_text", str(data))

    return str(data)


def format_travel_response(data) -> str:
    """Format travel plan data into readable text."""
    if not data:
        return "抱歉，无法生成旅游计划"

    if isinstance(data, dict):
        return data.get("formatted_text", str(data))

    return str(data)


@router.post("/stream")
async def chat_stream(request: ChatRequest):
    """Stream chat response using SSE."""
    return StreamingResponse(
        generate_stream(request.message, request.session_id),
        media_type="text/event-stream"
    )


@router.post("/chat")
async def chat(request: ChatRequest):
    """Non-streaming chat endpoint."""
    session_id = request.session_id or str(uuid.uuid4())

    with RequestTracer(request_id=session_id, request_data={'message': request.message}) as tracer:
        intent_parser = get_intent_parser()
        dispatcher = get_skill_dispatcher()

        tracer.begin_step('intent_parsing', {'input': request.message})
        intent = await intent_parser.parse(request.message)
        tracer.end_step('intent_parsing', {
            'type': intent.type.value,
            'confidence': intent.confidence,
            'parameters': intent.parameters
        })

        skill_results = {}

        if intent.type == IntentType.WEATHER_QUERY:
            tracer.begin_step('skill_weather_query', {'params': intent.parameters})
            log_step("Executing weather_query skill")
            weather_result = await dispatcher.dispatch_single(
                "weather_query", intent.parameters
            )
            skill_results["weather_query"] = weather_result.data
            tracer.end_step('skill_weather_query', {
                'success': weather_result.success,
                'data': weather_result.data
            }, error=None if weather_result.success else weather_result.error)
            content = format_weather_response(weather_result.data)

        elif intent.type == IntentType.TRAVEL_PLAN:
            tracer.begin_step('skill_travel_planner', {'params': intent.parameters})
            log_step("Executing travel_planner skill")
            travel_result = await dispatcher.dispatch_single(
                "travel_planner", intent.parameters
            )
            skill_results["travel_planner"] = travel_result.data
            tracer.end_step('skill_travel_planner', {
                'success': travel_result.success,
                'data': travel_result.data
            }, error=None if travel_result.success else travel_result.error)
            content = format_travel_response(travel_result.data)

        elif intent.type == IntentType.COMBINED:
            weather_params = intent.parameters.copy()
            travel_params = intent.parameters.copy()

            tracer.begin_step('skill_weather_query', {'params': weather_params})
            weather_result = await dispatcher.dispatch_single("weather_query", weather_params)
            skill_results["weather_query"] = weather_result.data
            tracer.end_step('skill_weather_query', {'success': weather_result.success})

            if weather_result.success and weather_result.data:
                travel_params["weather_data"] = weather_result.data

            tracer.begin_step('skill_travel_planner', {'params': travel_params})
            travel_result = await dispatcher.dispatch_single("travel_planner", travel_params)
            skill_results["travel_planner"] = travel_result.data
            tracer.end_step('skill_travel_planner', {'success': travel_result.success})

            weather_text = format_weather_response(weather_result.data)
            travel_text = format_travel_response(travel_result.data)
            content = f"{weather_text}\n\n{travel_text}"

        else:
            content = f"您好！收到您的消息：{request.message}。我可以帮您查询天气或制定旅游计划。"

        result = {
            "session_id": session_id,
            "content": content,
            "skill_results": skill_results,
            "usage": {
                "prompt_tokens": len(request.message),
                "completion_tokens": len(content),
                "total_tokens": len(request.message) + len(content)
            }
        }
        tracer.set_result(result)
        return result
