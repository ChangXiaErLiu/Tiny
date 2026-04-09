# TinyBill - Declarative Skill-Based AI Assistant

<div align="center">

![TinyBill](https://img.shields.io/badge/TinyBill-v2.0.0-6366f1?style=for-the-badge)
![Python](https://img.shields.io/badge/Python-3.10+-4FC08D?style=flat-square&logo=python)
![Vue](https://img.shields.io/badge/Vue-3.4-42B883?style=flat-square&logo=vue.js)
![FastAPI](https://img.shields.io/badge/FastAPI-0.109-009688?style=flat-square&logo=fastapi)
![License](https://img.shields.io/badge/License-MIT-FF6B6B?style=for-the-badge)

**A lightweight, highly extensible AI assistant framework based on the declarative Skill development paradigm**

[English](./README_EN.md) | [简体中文](./README.md)

</div>

---

## 📖 Introduction

TinyBill is an example project for learning the **Skill/Agent development paradigm**. It demonstrates how to:

- 🎯 **Declarative Skill Definition** - Describe skill metadata via `SKILL.md`
- 🧠 **Intent Understanding** - Recognize user intent and route to corresponding skills
- 🔧 **Skill Execution** - Execute logic through `script.py`
- 📡 **Streaming Response** - SSE for typewriter effect
- 🎨 **Modern Frontend** - Vue 3 + creative interactive animations

> **Learning Objective**: Understand core concepts of Skill framework, master modular design of Agent systems

---

## 🏗️ System Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                        TinyBill Architecture                      │
└─────────────────────────────────────────────────────────────────┘

  ┌──────────────┐         ┌──────────────┐         ┌──────────────┐
  │   Frontend   │         │   FastAPI    │         │    Skills    │
  │   (Vue 3)   │◄──────►│   Backend    │◄──────►│   (Python)   │
  └──────────────┘   SSE   └──────────────┘ subprocess └──────────────┘
                          │
                          ▼
                  ┌──────────────┐
                  │IntentParser  │
                  │(Intent Parse)│
                  └──────────────┘
                          │
                          ▼
                  ┌──────────────┐
                  │SkillDispatcher│
                  │(Skill Router)│
                  └──────────────┘
                          │
              ┌────────────┴────────────┐
              ▼                         ▼
      ┌──────────────┐          ┌──────────────┐
      │weather_query │          │travel_planner│
      │  (Weather)   │          │  (Travel)    │
      └──────────────┘          └──────────────┘
```

---

## 📁 Project Structure

```
hobbit/
├── backend/                          # Python Backend
│   ├── app/
│   │   ├── main.py                  # FastAPI app entry
│   │   ├── config.py                # Configuration
│   │   │
│   │   ├── api/v1/                 # API Endpoints
│   │   │   ├── chat.py             # Chat API (SSE streaming)
│   │   │   ├── skill.py            # Skill management
│   │   │   ├── health.py            # Health check
│   │   │   └── trace.py             # Request tracing
│   │   │
│   │   ├── core/                    # Core Modules
│   │   │   ├── agent/
│   │   │   │   ├── intent_parser.py # Intent parser
│   │   │   │   ├── skill_dispatcher.py # Skill dispatcher
│   │   │   │   └── base.py          # Data models
│   │   │   │
│   │   │   ├── skill/
│   │   │   │   ├── registry.py     # Skill registry
│   │   │   │   ├── executor.py      # Skill executor
│   │   │   │   └── base.py          # Skill models
│   │   │   │
│   │   │   └── tracing.py           # Request tracing system
│   │   │
│   │   ├── skills/                  # 🔑 Declarative Skills
│   │   │   ├── weather_query/       # Weather skill
│   │   │   │   ├── SKILL.md         # Skill metadata
│   │   │   │   ├── script.py        # Execution script
│   │   │   │   └── reference/       # Reference data
│   │   │   │
│   │   │   ├── travel_planner/     # Travel planner skill
│   │   │   │   ├── SKILL.md
│   │   │   │   ├── script.py
│   │   │   │   └── reference/
│   │   │   │
│   │   │   └── deepseek_llm/        # LLM skill
│   │   │       ├── SKILL.md
│   │   │       └── script.py
│   │   │
│   │   └── schemas/                 # Pydantic models
│   │
│   ├── tests/                       # Test files
│   ├── pyproject.toml              # Poetry config
│   └── .env.example                # Env template
│
├── frontend/                        # Vue 3 Frontend
│   ├── src/
│   │   ├── views/
│   │   │   └── ChatPage.vue        # Main chat page
│   │   │
│   │   ├── components/
│   │   │   ├── ChatMessage.vue     # Message bubble
│   │   │   ├── SkillStatus.vue     # Skill status badge
│   │   │   └── MarkdownRenderer.vue # Markdown renderer
│   │   │
│   │   ├── stores/
│   │   │   └── chat.ts             # Pinia store
│   │   │
│   │   ├── api/
│   │   │   └── client.ts           # API client
│   │   │
│   │   ├── composables/             # Vue Composables
│   │   │   └── useSkillStatus.ts
│   │   │
│   │   ├── types/
│   │   │   └── skill.ts            # TypeScript types
│   │   │
│   │   └── App.vue                 # Root component
│   │
│   ├── vite.config.ts              # Vite config
│   └── package.json
│
└── README.md                        # This file
```

---

## 🔑 Core Concepts

### 1. Declarative Skill

Each Skill is a directory containing:

```
skill_name/
├── SKILL.md       # 🎯 Skill metadata (required)
├── script.py      # 🔧 Execution script (required)
└── reference/    # 📚 Reference data (optional)
```

**SKILL.md Structure**:

```markdown
# Skill Name

## Version
1.0.0

## Description
Skill description...

## Use Cases
- Use case 1
- Use case 2

## Usage Guide
### Step 1: ...
### Step 2: ...

## Parameters
- `param1` (string, Required): Parameter description
- `param2` (integer, Optional): Parameter description

## Precautions
- Precaution 1
- Precaution 2
```

### 2. Skill Lifecycle

```
┌─────────────┐    ┌─────────────┐    ┌─────────────┐    ┌─────────────┐
│   Register  │───►│    Load     │───►│   Execute   │───►│   Return    │
│  (Startup)  │    │  (Runtime) │    │(subprocess)│    │   Result    │
└─────────────┘    └─────────────┘    └─────────────┘    └─────────────┘
```

### 3. Intent Parsing

Recognize user intent and map to corresponding skills:

| Intent Type | Maps To | Trigger Keywords |
|-------------|---------|-----------------|
| `WEATHER_QUERY` | weather_query | weather, temperature, umbrella |
| `TRAVEL_PLAN` | travel_planner | travel, itinerary, plan |
| `COMBINED` | weather_query + travel_planner | combined needs |

---

## 🚀 Quick Start

### Requirements

- Python 3.10+
- Node.js 18+
- npm or yarn

### 1. Clone Project

```bash
cd hobbit
```

### 2. Configure Backend

```bash
cd backend

# Copy environment template
cp .env.example .env

# Edit .env with your API Keys
# HEFENG_WEATHER_KEY=your_hefeng_key
# DEEPSEEK_API_KEY=your_deepseek_key
```

### 3. Install Backend Dependencies

```bash
# Using Poetry
poetry install

# Or using pip
pip install -r requirements.txt
```

### 4. Install Frontend Dependencies

```bash
cd frontend
npm install
```

### 5. Start Services

**Terminal 1 - Backend**:
```bash
cd backend
poetry run uvicorn app.main:app --reload --port 8000
```

**Terminal 2 - Frontend**:
```bash
cd frontend
npm run dev
```

### 6. Access App

Open browser: http://localhost:3000

---

## 🎯 Usage Examples

### Weather Query

```
User: What's the weather in Nanning tomorrow?
System: Recognizes WEATHER_QUERY intent
     → Calls weather_query skill
     → Returns formatted weather forecast
```

### Travel Planning

```
User: Help me plan a 3-day trip to Nanning
System: Recognizes TRAVEL_PLAN intent
     → Calls travel_planner skill
     → Returns daily itinerary
```

### Combined Query

```
User: Do I need an umbrella for a 3-day trip to Guilin?
System: Recognizes COMBINED intent
     → First calls weather_query for weather
     → Then calls travel_planner for itinerary
     → Returns combined response
```

---

## 📡 API Documentation

After starting, visit: http://localhost:8000/docs

### Core Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `POST /api/v1/chat/stream` | POST | Streaming chat (SSE) |
| `POST /api/v1/chat/chat` | POST | Non-streaming chat |
| `GET /api/v1/skills` | GET | List all skills |
| `GET /api/v1/skills/{name}` | GET | Get skill details |
| `GET /api/v1/health` | GET | Health check |
| `GET /api/v1/traces` | GET | List traces |
| `GET /api/v1/traces/{id}` | GET | Get trace details |

### SSE Event Stream

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
data: {"content": "D"}

event: content
data: {"content": "a"}

event: done
data: {"session_id": "xxx", "usage": {...}}
```

---

## 🛠️ Adding a New Skill

### Step 1: Create Skill Directory

```
backend/app/skills/
└── my_new_skill/
    ├── SKILL.md
    ├── script.py
    └── reference/
        └── data.json
```

### Step 2: Write SKILL.md

```markdown
# My New Skill

## Version
1.0.0

## Description
Description of this skill...

## Use Cases
- Use case 1
- Use case 2

## Usage Guide
### Step 1: Prepare parameters
### Step 2: Execute logic
### Step 3: Return result

## Parameters
- `input` (string, Required): Input parameter

## Precautions
- Precaution
```

### Step 3: Write script.py

```python
"""My New Skill - Script"""
import json
import sys

def main():
    # Read input from stdin
    input_data = json.loads(sys.stdin.read())

    # Process logic
    result = {
        "data": {"message": "Result message"},
        "success": True
    }

    # Output JSON to stdout
    print(json.dumps(result, ensure_ascii=False))

if __name__ == "__main__":
    main()
```

### Step 4: Restart Service

Skills are automatically registered at startup - no manual addition needed.

---

## 🎨 Frontend Features

| Feature | Description |
|---------|-------------|
| Streaming Typewriter | SSE character-by-character display |
| Markdown Rendering | Code highlighting, tables, lists |
| Copy Button | Hover to show copy button |
| Skill Status | Real-time skill execution status |
| Creative Animations | Bubble pop-in, send animation |
| Easter Eggs | Specific inputs trigger reactions |
| Idle Robot | Empty state animation |
| Command Palette | ⌘K to open |

---

## 📚 Learning Points

### Skill Framework Core

1. **Declarative Definition**: Metadata separated from logic
2. **Hot Registration**: Add new Skills without modifying framework code
3. **Standardized I/O**: JSON via stdin/stdout
4. **Composability**: Multiple Skills can work together

### Agent System Components

```
Agent System
├── Intent Parser    # Understand user intent
├── Skill Registry  # Manage skill registration
├── Skill Dispatcher # Route to corresponding skill
├── Skill Executor   # Execute skill scripts
└── Response Format  # Format output
```

---

## 🔧 Configuration

### Environment Variables (.env)

```env
# API Keys
HEFENG_WEATHER_KEY=     # HeFeng Weather API Key
AMAP_KEY=              # AMap API Key
DEEPSEEK_API_KEY=       # DeepSeek API Key

# Timeouts (milliseconds)
WEATHER_API_TIMEOUT=5000
TRAVEL_API_TIMEOUT=5000
LLM_TIMEOUT=60000

# Logging
LOG_LEVEL=INFO
```

### Skill Parameter Passing

```python
# Backend -> Skill
{
    "city": "Nanning",
    "days": 3,
    "_context": {...}  # Framework-injected context
}

# Skill -> Backend
{
    "data": {...},      # Skill-returned data
    "success": True
}
```

---

## 📝 Development Guide

### Code Standards

- Python: PEP 8
- TypeScript: ESLint + Prettier
- Vue: Composition API

### Testing

```bash
# Backend tests
cd backend
poetry run pytest tests/

# Frontend type check
cd frontend
npm run typecheck
```

### Build

```bash
# Frontend production build
cd frontend
npm run build
```

---

## 🤝 Contributing

Issues and Pull Requests are welcome!

1. Fork this repository
2. Create feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to branch (`git push origin feature/AmazingFeature`)
5. Create Pull Request

---

## 📄 License

This project is MIT licensed - see [LICENSE](LICENSE) file

---

## 🙏 Acknowledgments

- [FastAPI](https://fastapi.tiangolo.com/) - Modern Python Web Framework
- [Vue.js](https://vuejs.org/) - Progressive JavaScript Framework
- [QWeather](https://www.qweather.com/) - Weather Data Service
- [DeepSeek](https://www.deepseek.com/) - Large Language Model

---

<div align="center">

**Made with ❤️ by TinyBill Team**

</div>
