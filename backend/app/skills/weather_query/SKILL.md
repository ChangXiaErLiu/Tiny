# Weather Query Skill

## Version
1.0.0

## Description
天气查询技能用于获取指定城市的实时天气信息和未来天气预报。当用户询问"天气怎么样"、"气温多少"、"需要带伞吗"等问题时使用此技能。

## Use Cases
- 查询城市当前天气（温度、湿度、风力、天气状况）
- 查询未来1-7天的天气预报
- 根据天气情况给出出行建议（如：带伞、加衣、防晒）
- 支持同时查询多个城市或对比不同城市天气

## Usage Guide

### Step 1: Extract Parameters
从用户输入中提取以下参数：
- `city` (必填): 城市名称，如"南宁"、"桂林"
- `days` (可选): 预报天数，默认3天，最大7天

### Step 2: Call Weather API
使用和风天气 API 或其他天气数据源获取天气信息。

API Endpoint: `https://devapi.qweather.com/v7/weather/now`
API Endpoint: `https://devapi.qweather.com/v7/weather/{days}d`

### Step 3: Format Response
将 API 返回的原始数据格式化为人类可读的天气描述。

### Step 4: Generate Suggestions
根据天气数据生成实用建议（如：出行注意事项、服装建议等）

## Parameters
- `city` (string, Required): 要查询的城市名称
- `days` (integer, Optional): 预报天数，默认3天

## Precautions
- 如果用户没有指定城市，优先从上下文中推断或询问用户
- 如果 API 调用失败，返回友好的错误提示，不要暴露技术细节
- 温度单位统一使用摄氏度
- 天气预报仅供参考，重大活动需参考官方预报
- 雨天出行提醒用户带伞，晴天提醒防晒

## Reference Materials
参考文档位于 `./reference/` 目录：
- `city_codes.json`: 常用城市代码对照表

## Execution Script
执行脚本位于 `./script.py`
