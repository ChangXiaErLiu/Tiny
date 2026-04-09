# TinyBill - 基于声明式技能框架的智能助手

<div align="center">

![TinyBill](https://img.shields.io/badge/TinyBill-v2.0.0-6366f1?style=for-the-badge)
![Python](https://img.shields.io/badge/Python-3.10+-4FC08D?style=flat-square\&logo=python)
![Vue](https://img.shields.io/badge/Vue-3.4-42B883?style=flat-square\&logo=vue.js)
![FastAPI](https://img.shields.io/badge/FastAPI-0.109-009688?style=flat-square\&logo=fastapi)
![License](https://img.shields.io/badge/License-MIT-FF6B6B?style=flat-square)

**一个轻量级、高扩展性的智能助手框架，基于声明式 Skill 开发范式**

[English](./README_EN.md) | 简体中文

</div>

***

## 📖 项目简介

TinyBill 是一个学习 **Skill/Agent 开发范式** 的示例项目。它展示瞭如何：

- 🎯 **声明式定义技能** - 通过 `SKILL.md` 描述技能元信息
- 🧠 **意图理解** - 识别用户意图并路由到对应技能
- 🔧 **技能执行** - 通过 `script.py` 执行具体逻辑
- 📡 **流式响应** - SSE 实现打字机效果
- 🎨 **现代化前端** - Vue 3 + 创意交互动画

> **学习目标**：理解 Skill 框架的核心概念，掌握 Agent 系统的模块化设计

***

## 🏗️ 系统架构

```
┌─────────────────────────────────────────────────────────────────┐
│                         TinyBill 架构图                           │
└─────────────────────────────────────────────────────────────────┘

  ┌──────────────┐         ┌──────────────┐         ┌──────────────┐
  │   Frontend   │         │   FastAPI    │         │   Skills     │
  │   (Vue 3)   │◄──────►│   Backend    │◄──────►│   (Python)   │
  └──────────────┘  SSE    └──────────────┘  subprocess  └──────────────┘
                           │
                           ▼
                   ┌──────────────┐
                   │IntentParser  │
                   │(意图理解)     │
                   └──────────────┘
                           │
                           ▼
                   ┌──────────────┐
                   │SkillDispatcher│
                   │(技能调度)     │
                   └──────────────┘
                           │
              ┌────────────┴────────────┐
              ▼                         ▼
      ┌──────────────┐          ┌──────────────┐
      │weather_query │          │travel_planner │
      │  (天气技能)   │          │  (旅游技能)   │
      └──────────────┘          └──────────────┘
```

***

## 📁 项目结构

```
hobbit/
├── backend/                          # Python 后端
│   ├── app/
│   │   ├── main.py                  # FastAPI 应用入口
│   │   ├── config.py                # 配置管理
│   │   │
│   │   ├── api/v1/                 # API 端点
│   │   │   ├── chat.py             # 聊天接口 (SSE流式)
│   │   │   ├── skill.py            # 技能管理
│   │   │   ├── health.py            # 健康检查
│   │   │   └── trace.py             # 请求追踪
│   │   │
│   │   ├── core/                    # 核心模块
│   │   │   ├── agent/
│   │   │   │   ├── intent_parser.py # 意图解析器
│   │   │   │   ├── skill_dispatcher.py # 技能调度器
│   │   │   │   └── base.py          # 数据模型
│   │   │   │
│   │   │   ├── skill/
│   │   │   │   ├── registry.py     # 技能注册中心
│   │   │   │   ├── executor.py      # 技能执行器
│   │   │   │   └── base.py          # 技能数据模型
│   │   │   │
│   │   │   └── tracing.py           # 请求追踪系统
│   │   │
│   │   ├── skills/                  # 🔑 声明式技能目录
│   │   │   ├── weather_query/       # 天气查询技能
│   │   │   │   ├── SKILL.md         # 技能元信息定义
│   │   │   │   ├── script.py        # 执行脚本
│   │   │   │   └── reference/       # 参考数据
│   │   │   │
│   │   │   ├── travel_planner/      # 旅游规划技能
│   │   │   │   ├── SKILL.md
│   │   │   │   ├── script.py
│   │   │   │   └── reference/
│   │   │   │
│   │   │   └── deepseek_llm/        # LLM 技能
│   │   │       ├── SKILL.md
│   │   │       └── script.py
│   │   │
│   │   └── schemas/                 # Pydantic 模型
│   │
│   ├── tests/                       # 测试文件
│   ├── pyproject.toml              # Poetry 配置
│   └── .env.example                # 环境变量示例
│
├── frontend/                        # Vue 3 前端
│   ├── src/
│   │   ├── views/
│   │   │   └── ChatPage.vue        # 主聊天页面
│   │   │
│   │   ├── components/
│   │   │   ├── ChatMessage.vue     # 消息气泡
│   │   │   ├── SkillStatus.vue     # 技能状态徽章
│   │   │   └── MarkdownRenderer.vue # Markdown 渲染
│   │   │
│   │   ├── stores/
│   │   │   └── chat.ts             # Pinia 状态管理
│   │   │
│   │   ├── api/
│   │   │   └── client.ts           # API 客户端
│   │   │
│   │   ├── composables/             # Vue Composables
│   │   │   └── useSkillStatus.ts
│   │   │
│   │   ├── types/
│   │   │   └── skill.ts            # TypeScript 类型
│   │   │
│   │   └── App.vue                 # 根组件
│   │
│   ├── vite.config.ts              # Vite 配置
│   └── package.json
│
└── README.md                        # 本文档
```

***

## 🔑 核心概念

### 1. 声明式 Skill

每个 Skill 是一个目录，包含：

```
skill_name/
├── SKILL.md       # 🎯 技能元信息（必填）
├── script.py      # 🔧 执行脚本（必填）
└── reference/    # 📚 参考资料（可选）
```

**SKILL.md 结构**：

```markdown
# Skill Name

## Version
1.0.0

## Description
技能描述...

## Use Cases
- 用例1
- 用例2

## Usage Guide
### Step 1: ...
### Step 2: ...

## Parameters
- `param1` (string, Required): 参数描述
- `param2` (integer, Optional): 参数描述

## Precautions
- 注意事项1
- 注意事项2
```

### 2. Skill 生命周期

```
┌─────────────┐    ┌─────────────┐    ┌─────────────┐    ┌─────────────┐
│   Register  │───►│    Load     │───►│   Execute   │───►│   Return    │
│   (启动时)   │    │  (运行时)   │    │ (subprocess)│    │   Result    │
└─────────────┘    └─────────────┘    └─────────────┘    └─────────────┘
```

### 3. 意图解析 (Intent Parser)

识别用户意图并映射到对应技能：

| Intent Type     | 映射技能                             | 触发关键词    |
| --------------- | -------------------------------- | -------- |
| `WEATHER_QUERY` | weather\_query                   | 天气、气温、带伞 |
| `TRAVEL_PLAN`   | travel\_planner                  | 旅游、行程、攻略 |
| `COMBINED`      | weather\_query + travel\_planner | 综合需求     |

***

## 🚀 快速开始

### 环境要求

- Python 3.10+
- Node.js 18+
- npm 或 yarn

### 1. 克隆项目

```bash
cd hobbit
```

### 2. 配置后端

```bash
cd backend

# 复制环境变量模板
cp .env.example .env

# 编辑 .env 填入 API Key
# HEFENG_WEATHER_KEY=你的和风天气Key
# DEEPSEEK_API_KEY=你的DeepSeek Key
# 
```

### 3. 安装后端依赖

```bash
# 使用 Poetry
poetry install

# 或使用 pip
pip install -r requirements.txt
```

### 4. 安装前端依赖

```bash
cd frontend
npm install
```

### 5. 启动服务

**终端 1 - 后端**：

```bash
cd backend
poetry run uvicorn app.main:app --reload --port 8000
```

**终端 2 - 前端**：

```bash
cd frontend
npm run dev
```

### 6. 访问应用

打开浏览器访问：<http://localhost:3000>

***

## 🎯 使用示例

### 天气查询

```
用户：南宁明天天气怎么样？
系统：识别为 WEATHER_QUERY 意图
     → 调用 weather_query 技能
     → 返回格式化的天气预报
```

### 旅游规划

```
用户：帮我制定一个三天的南宁旅游计划
系统：识别为 TRAVEL_PLAN 意图
     → 调用 travel_planner 技能
     → 返回每日行程安排
```

### 综合查询

```
用户：去桂林玩3天需要带伞吗？
系统：识别为 COMBINED 意图
     → 先调用 weather_query 获取天气
     → 再调用 travel_planner 生成行程
     → 综合返回
```

***

## 📡 API 文档

启动后访问：<http://localhost:8000/docs>

### 核心接口

| 端点                          | 方法   | 说明        |
| --------------------------- | ---- | --------- |
| `POST /api/v1/chat/stream`  | POST | 流式聊天（SSE） |
| `POST /api/v1/chat/chat`    | POST | 非流式聊天     |
| `GET /api/v1/skills`        | GET  | 列出所有技能    |
| `GET /api/v1/skills/{name}` | GET  | 获取技能详情    |
| `GET /api/v1/health`        | GET  | 健康检查      |
| `GET /api/v1/traces`        | GET  | 请求追踪列表    |
| `GET /api/v1/traces/{id}`   | GET  | 追踪详情      |

### SSE 事件流

```
event: session_start
data: {"session_id": "xxx"}

event: intent_parsed
data: {"type": "TRAVEL_PLAN", "confidence": 0.85, ...}

event: skill_start
data: {"skill": "travel_planner", "status": "start"}

event: skill_end
data: {"skill": "travel_planner", "status": "end", "success": true}

event: content
data: {"content": "第"}

event: content
data: {"content": "一"}

event: done
data: {"session_id": "xxx", "usage": {...}}
```

***

## 🛠️ 如何添加新技能

### Step 1: 创建技能目录

```
backend/app/skills/
└── my_new_skill/
    ├── SKILL.md
    ├── script.py
    └── reference/
        └── data.json
```

### Step 2: 编写 SKILL.md

```markdown
# My New Skill

## Version
1.0.0

## Description
这是一个新技能的描述...

## Use Cases
- 使用场景1
- 使用场景2

## Usage Guide
### Step 1: 准备参数
### Step 2: 执行逻辑
### Step 3: 返回结果

## Parameters
- `input` (string, Required): 输入参数

## Precautions
- 注意事项
```

### Step 3: 编写 script.py

```python
"""My New Skill - Script"""
import json
import sys

def main():
    # 从 stdin 读取输入
    input_data = json.loads(sys.stdin.read())

    # 处理逻辑
    result = {
        "data": {"message": "处理结果"},
        "success": True
    }

    # 输出 JSON 到 stdout
    print(json.dumps(result, ensure_ascii=False))

if __name__ == "__main__":
    main()
```

### Step 4: 重启服务

技能会在启动时自动注册，无需手动添加。

***

## 🎨 前端特性

| 特性          | 说明           |
| ----------- | ------------ |
| 流式打字效果      | SSE 逐字显示     |
| Markdown 渲染 | 支持代码高亮、表格、列表 |
| 复制功能        | hover 显示复制按钮 |
| 技能状态        | 实时显示技能执行状态   |
| 创意动画        | 气泡弹入、发送动画    |
| 彩蛋系统        | 特定输入触发表情     |
| 懒散机器人       | 空状态动画        |
| 命令面板        | ⌘K 打开        |

***

## 📚 学习要点

### Skill 框架核心

1. **声明式定义**：元信息与逻辑分离
2. **热注册**：新增 Skill 无需修改框架代码
3. **标准化输入输出**：JSON via stdin/stdout
4. **可组合性**：多个 Skill 可以协同工作

### Agent 系统组件

```
Agent System
├── Intent Parser    # 理解用户意图
├── Skill Registry  # 管理技能注册
├── Skill Dispatcher # 路由到对应技能
├── Skill Executor   # 执行技能脚本
└── Response Format  # 格式化输出
```

***

## 🔧 配置说明

### 环境变量 (.env)

```env
# API Keys
HEFENG_WEATHER_KEY=     # 和风天气 API Key
AMAP_KEY=              # 高德地图 API Key
DEEPSEEK_API_KEY=      # DeepSeek API Key

# 超时配置
WEATHER_API_TIMEOUT=5000
TRAVEL_API_TIMEOUT=5000
LLM_TIMEOUT=60000

# 日志
LOG_LEVEL=INFO
```

### 技能参数传递

```python
# 后端 -> 技能
{
    "city": "南宁",
    "days": 3,
    "_context": {...}  # 框架注入的上下文
}

# 技能 -> 后端
{
    "data": {...},      # 技能返回的数据
    "success": True
}
```

***

## 📝 开发指南

### 代码规范

- Python: PEP 8
- TypeScript: ESLint + Prettier
- Vue: Composition API

### 测试

```bash
# 后端测试
cd backend
poetry run pytest tests/

# 前端类型检查
cd frontend
npm run typecheck
```

### 构建

```bash
# 前端生产构建
cd frontend
npm run build
```

***

## 🤝 贡献指南

欢迎提交 Issue 和 Pull Request！

***

## 📄 许可证

本项目基于 MIT 许可证 

***

## 🙏 致谢

- [FastAPI](https://fastapi.tiangolo.com/) - 现代 Python Web 框架
- [Vue.js](https://vuejs.org/) - 渐进式 JavaScript 框架
- [、和风天气](https://www.qweather.com/) - 天气数据服务
- [DeepSeek](https://www.deepseek.com/) - 大语言模型

***

