# DeepSeek LLM Skill

## Version
1.0.0

## Description
DeepSeek LLM 技能使用 DeepSeek 大语言模型生成自然、流畅的回复。当其他技能需要生成自然语言描述、总结数据、或需要 AI 生成创意内容时，可以调用此技能。

## Use Cases
- 将结构化数据（如天气、行程）转化为自然语言描述
- 生成创意性内容（旅游文案、推荐语）
- 回答用户的一般性问题
- 对话式交互和闲聊
- 内容总结和归纳

## Usage Guide

### Step 1: Prepare Prompt
根据任务类型准备合适的提示词：
- 系统提示词（可选）：定义 AI 的角色和能力
- 用户提示词：要回答的问题或任务描述

### Step 2: Call DeepSeek API
使用 DeepSeek Chat API 生成回复。

API Endpoint: `https://api.deepseek.com/chat/completions`
Model: `deepseek-chat`

### Step 3: Process Response
提取 API 返回的 `content` 字段作为生成结果。

### Step 4: Return Format
Skill 输出包含：
- `content`: 生成的文本内容
- `usage`: Token 使用统计
- `model`: 使用的模型名称

## Parameters
- `prompt` (string, Required): 用户输入的提示词
- `system_prompt` (string, Optional): 系统提示词，定义 AI 角色
- `temperature` (number, Optional): 生成温度，0.0-2.0，默认0.7
- `max_tokens` (integer, Optional): 最大生成 Token 数，默认2000
- `stream` (boolean, Optional): 是否使用流式输出，默认false

## Precautions
- 提示词应该清晰、具体，避免歧义
- 敏感内容需要进行过滤和检查
- 合理设置 temperature，高创造性任务用较高值，准确性任务用较低值
- 流式输出时需要特殊处理 SSE 事件
- API 调用失败时要有降级策略

## Reference Materials
- `system_prompts.json`: 常用系统提示词模板

## Execution Script
执行脚本位于 `./script.py`
