# MangaCraft 🎨

### AI-Powered Manga Panel Assistant

MangaCraft is an AI-powered workspace designed to help manga artists analyze panels, maintain project-specific context, and generate visual references.

The project evolved from a simple conversational AI assistant into a **tool-using AI agent with persistent Project Intelligence**, combining LLM reasoning, multimodal understanding, SQLite persistence, and image generation.

> **Current Version: V2 — AI Agent + Project Intelligence**

---

## ✨ What is MangaCraft?

Creating manga involves more than drawing individual panels. Artists need to maintain consistency in characters, poses, composition, visual decisions, and story context across an entire project.

MangaCraft is designed around this problem.

Instead of treating every conversation as isolated, MangaCraft provides a **project-based workspace** where the AI can work with:

* Manga panels
* Project memories
* Conversations
* Generated references
* Character and design information
* Visual analysis

The goal is to make the AI assistant behave more like a **project-aware creative assistant** rather than a simple chatbot.

---

## 🚀 Features

### 🤖 AI Agent with Tool Calling

MangaCraft uses an LLM-driven tool-selection architecture.

The user message is provided to the LLM together with the available tools, and the model decides whether a tool is required.

The current agent has **7 tools**:

#### Project Intelligence

* `save_project_memory`
* `get_project_memory`
* `search_project`
* `get_project_context`

#### Visual & Generation

* `analyze_panel`
* `composition_analysis`
* `generate_reference`

Tool selection uses `tool_choice="auto"` rather than application-level keyword routing.

---

### 🧠 Project Memory

MangaCraft maintains persistent project-specific information using SQLite.

Memory can contain information such as:

* Character details
* Story information
* Relationships
* Design decisions
* Art-style decisions
* Other project-specific facts

For example:

> "Kageyama always wears a black jacket."

The information can be stored as Project Memory and retrieved later when relevant.

This allows project knowledge to persist beyond a single conversation.

---

### 🔎 Project Context & Memory Search

The agent can retrieve information from the current project when required.

Different retrieval operations serve different purposes:

* **Get Project Memory** — retrieve stored project memories
* **Search Project** — find a specific established fact
* **Get Project Context** — retrieve a broader project overview

Project data is isolated by project, preventing memories from one project from being returned for another project.

---

### 🖼️ Multimodal Panel Analysis

Users can upload manga panels and ask the AI to analyze them.

MangaCraft can use the uploaded panel for tasks such as:

* Panel description
* Character positioning
* Pose
* Facial expressions
* Camera angle
* Composition
* Perspective
* Lighting
* Visual relationships

The vision model receives the image together with the user's request.

---

### 🎬 Composition Analysis

MangaCraft includes a dedicated composition-analysis tool for examining visual structure.

It can help analyze aspects such as:

* Camera angle
* Shot type
* Character placement
* Spatial relationships
* Visual depth
* Composition
* Perspective

---

### 🎨 AI Reference Generation

MangaCraft can use an existing panel as a visual reference for image generation.

The workflow is intentionally separated into two stages:

1. The AI understands the user's generation request.
2. The application performs the actual image generation.

If the request is too vague, the agent can ask clarification questions before capturing the generation request.

This prevents the system from blindly generating an image from an underspecified request.

---

### 💬 Multiple Conversations per Project

A project can contain multiple conversations.

For example:

```text
Project: My Manga
│
├── Conversation 1 — Character Design
├── Conversation 2 — Panel Analysis
├── Conversation 3 — Story Planning
└── Conversation 4 — Reference Generation
```

Starting a **New Chat** creates another conversation under the same project.

Existing conversations can be reopened later.

---

### 🧾 Conversation Persistence

Conversation messages are stored in SQLite.

When a conversation is reopened, its previous messages can be restored.

This allows users to continue working from where they previously stopped.

---

### ⏳ Conversation Limits

To prevent conversations from growing indefinitely, MangaCraft currently limits a conversation to **25 turns**.

When the limit is reached, the conversation is locked and the user is asked to start a New Chat.

This keeps individual conversations bounded while allowing new conversations within the same project.

---

### ⚡ Streaming Responses

Final responses are streamed progressively to the Gradio interface rather than appearing only after the entire response has been generated.

This makes the interaction more responsive.

---

### 🛡️ Rate Limiting

MangaCraft includes application-level rate limiting to prevent excessive LLM API calls.

Current configuration:

```text
10 LLM calls
per 60 seconds
per session
```

This helps control accidental repeated requests and API usage.

---

### 🚨 Error Handling

MangaCraft handles failures from external AI services and application-level operations, including:

* Vision model requests
* Image generation
* Invalid image paths
* Missing configuration
* External API failures

Instead of exposing raw exceptions to users, the application returns user-friendly error messages while logging the underlying failure for debugging.

---

### 🔄 Project & Conversation Restoration

MangaCraft remembers the user's most recently opened project.

When the application is restarted, the previous project can be restored.

Projects retain their associated:

* Panels
* Conversations
* Project Memory
* Generated references

---

## 🏗️ Architecture

The current V2 architecture can be simplified as:

```text
                         ┌───────────────────┐
                         │      Gradio UI    │
                         └─────────┬─────────┘
                                   │
                                   ▼
                         ┌───────────────────┐
                         │   Application     │
                         │      Layer        │
                         └─────────┬─────────┘
                                   │
                                   ▼
                         ┌───────────────────┐
                         │    LLM Agent      │
                         │   tool_choice=    │
                         │       "auto"      │
                         └─────────┬─────────┘
                                   │
              ┌────────────────────┼────────────────────┐
              │                    │                    │
              ▼                    ▼                    ▼
       Project Memory         Visual Tools       Generation Tool
              │                    │                    │
              └────────────────────┼────────────────────┘
                                   │
                                   ▼
                            ┌──────────────┐
                            │    SQLite    │
                            │   Database   │
                            └──────────────┘
```

The LLM decides which tool is appropriate, while the application remains responsible for things such as:

* Project selection
* Conversation limits
* Rate limiting
* Image/path validation
* Tool execution
* Database persistence
* Error handling

---

## 🗃️ Data Model

MangaCraft currently uses SQLite for persistence.

Main tables include:

```text
projects
panels
generated_references
conversations
messages
project_memory
```

The relationship is:

```text
Project
│
├── Panels
│
├── Conversations
│   └── Messages
│
├── Project Memory
│
└── Generated References
```

This structure keeps project-specific information isolated.

---

## 🛠️ Tech Stack

### UI

* Python
* Gradio

### AI / LLM

* OpenRouter
* OpenAI-compatible API
* Multimodal LLM capabilities

### Persistence

* Python
* SQLite
* Custom repository layer

### Image Generation

* Hugging Face Inference Providers
* FLUX.1-Kontext

### Development

* Git
* GitHub
* Python virtual environment

---

## 📁 Project Structure

```text
Manga-Craft/
│
├── app.py
├── config.py
├── llm.py
├── prompts.py
├── requirements.txt
├── MangaCraft_V1.ipynb
│
├── database/
│   ├── __init__.py
│   ├── database.py
│   ├── conversation_repository.py
│   ├── generated_reference_repository.py
│   ├── panel_repository.py
│   ├── project_memory_repository.py
│   ├── project_repository.py
│   └── test_conversations.py
│
├── tools/
│   ├── __init__.py
│   ├── panel_tools.py
│   └── project_memory_tools.py
│
├── utils/
│   └── image_utils.py
│
├── data/
│   ├── mangacraft.db
│   └── projects/
│
├── test_projects.py
├── test_project_memory.py
├── test_project_memory_tools.py
├── test_real_tool_selection.py
│
├── .gitignore
└── README.md
```

Local databases, uploaded project data, environment files,some test files and other runtime artifacts are excluded from Git.

Development and regression test scripts are kept in the repository.

---

## ⚙️ Local Setup

### 1. Clone the repository

```bash
git clone <your-github-repository-url>
cd Manga-Craft
```

### 2. Create a virtual environment

```bash
python -m venv .venv
```

Activate it on Windows:

```powershell
.venv\Scripts\activate
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

### 4. Configure environment variables

Create a `.env` file:

```env
OPENROUTER_API_KEY=your_openrouter_api_key
HF_TOKEN=your_huggingface_token
```

The current V2 LLM path uses **OpenRouter**.

If you prefer another inexpensive provider such as Google Gemini, the provider can be substituted by adapting the application's LLM configuration; Gemini is not currently the primary provider used by MangaCraft V2.

**Never commit API keys or `.env` to GitHub.**

### 5. Run MangaCraft

```bash
python app.py
```

The Gradio interface will start locally.

---

## 🔐 Environment Variables

| Variable             | Purpose                                          |
| -------------------- | ------------------------------------------------ |
| `OPENROUTER_API_KEY` | LLM API access                                   |
| `HF_TOKEN`           | Hugging Face authentication for image generation |

API keys should be stored as environment variables locally and as deployment secrets when deployed.

---

## 🧪 Testing

MangaCraft V2 was tested across the major application workflows, including:

* Normal conversations
* LLM tool selection
* Panel analysis
* Composition analysis
* Reference-generation clarification
* Reference-generation failure handling
* Project Memory save
* Project Memory retrieval
* Project Memory search
* Project Context
* Multiple conversations
* Conversation limits
* Rate limiting
* Project switching
* Project restoration
* SQLite persistence
* Error handling
* Streaming responses

The application was also tested after code cleanup and deployment-oriented filesystem path changes.

---

## ⚠️ Current Limitations

MangaCraft V2 is a learning-driven project and has several limitations.

* AI service usage depends on external API availability and credits.
* Image generation requires access to a supported Hugging Face inference service.
* SQLite is currently used instead of a production database.
* Authentication and user ownership are not implemented.
* The current UI is built with Gradio.
* Advanced semantic retrieval and vector-based RAG are not implemented.
* Persistent cloud storage requires additional deployment configuration.
* The current application is primarily designed as a single-user/project workspace rather than a multi-user production SaaS.

These limitations are intentionally outside the current V2 scope.

---

## 🔮 Future Direction

The next major architectural evolution is planned for V3.

Potential V3 work includes:

* React frontend
* FastAPI backend
* PostgreSQL
* Authentication
* User/project ownership
* Authorization
* Advanced rate and usage limits
* Embeddings
* Vector databases
* RAG
* Docker
* Production monitoring
* More advanced agent orchestration

V3 is planned as a progression from the foundations established in V2.

---

## 🎯 Why I Built MangaCraft

MangaCraft started as a way to understand how LLM applications work beyond a simple chatbot.

The project became an opportunity to learn and implement concepts such as:

* LLM APIs
* Tool calling
* Multimodal AI
* Persistent context
* SQLite
* AI agent workflows
* Image generation
* API usage control
* Error handling
* Application architecture

Rather than building isolated tutorial projects, MangaCraft combines these concepts into a single application built around a creative workflow.

The project was developed using concepts learned through AI engineering coursework and then extended into a custom application based on my own idea and implementation.

---

## 📌 Project Status

**MangaCraft V2 — AI Agent + Project Intelligence**

The current V2 implementation has completed regression and smoke testing.

The next step is deployment and real-world testing.
