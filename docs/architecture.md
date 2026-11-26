# MangaCraft V3 Architecture

## Current Architecture (V2)

```
Gradio UI (app.py)
    ↓
Python Application Logic
    ↓
SQLite Database (data/mangacraft.db)
    ↓
File System (data/projects/)
```

**V2 Components**:
- **Frontend**: Gradio interface
- **Backend**: Python (monolithic app.py)
- **Database**: SQLite
- **AI**: OpenRouter (LLM), OpenRouter Image API
- **Storage**: Local filesystem

## Planned V3 Architecture

```
React Frontend
    ↓ (HTTP/REST API)
FastAPI Backend
    ↓
Authentication & Authorization
    ↓
Services Layer
    ├── AI Service
    ├── Context Builder
    └── Memory Service
    ↓
Data Layer
    ├── MongoDB (Primary Database)
    │   ├── Users
    │   ├── Projects
    │   ├── Conversations
    │   ├── Messages
    │   ├── Project Memory
    │   ├── Panels
    │   └── Generated References
    └── Vector Search (MongoDB Atlas Vector Search)
    ↓
External Services
    ├── OpenRouter (LLM)
    ├── OpenRouter (Image Generation)
    └── Object Storage (S3-compatible)
```

## Component Relationships

### Frontend to Backend
```
React Components
    ↓ (axios HTTP client)
FastAPI Endpoints
    ↓ (authentication middleware)
Business Logic
```

### Authentication Flow
```
React Login/Register Pages
    ↓ (POST /auth/login or /auth/register)
FastAPI Auth Endpoints
    ↓ (bcrypt password hashing)
JWT Generation (python-jose)
    ↓ (token storage in localStorage - dev, httpOnly cookies - prod)
Token in Authorization Header (Bearer token)
    ↓ (authentication dependency)
Protected Routes
```

**Authentication Implementation Details:**
- **Password Hashing**: bcrypt (not passlib due to compatibility issues)
- **JWT Library**: python-jose[cryptography]
- **Token Storage**: localStorage (development), should use httpOnly cookies in production
- **Token Expiration**: 30 minutes (configurable)
- **Protected Routes**: FastAPI dependency injection with HTTPBearer
- **User Ownership**: Projects filtered by user_id, users can only access their own data
- **Frontend Auth**: AuthContext manages session state, logout, and token persistence

### Project Ownership
```
User
    ↓ (one-to-many)
Projects
    ↓ (one-to-many)
├── Conversations
├── Panels
├── Project Memory
└── Generated References
```

### AI Orchestration (V3.11 — implemented)
```
React ChatWorkspace
    ↓ POST /chat/stream  (JSON body)
FastAPI api/chat.py
    ↓ 1. save user message
    ↓ 2. services/context_builder.py -> project briefing
    ↓ 3. load recent messages (working memory)
    ↓ 4. services/ai_service.py -> OpenRouter (stream=True)
    ↓ StreamingResponse (text/event-stream)
React reads tokens via fetch + ReadableStream
    ↓ typewriter reveal -> live bubble + auto-scroll
Server accumulates tokens -> saves full assistant message on completion
```
- Two endpoints share the same context logic: `POST /chat/` (non-streaming) and `POST /chat/stream` (SSE streaming)
- Model fallback chain: `gemini-2.5-flash-lite` → `gemini-2.5-flash` on provider errors (e.g. 429)
- Context = SYSTEM_PROMPT + project briefing + most recent 20 messages

### AI Orchestration (planned before V3.11)
```
React Chat Interface
    ↓ (POST /api/ai/chat)
FastAPI AI Service
    ↓
Context Builder
    ├── Conversation History
    ├── Project Memory
    ├── RAG Retrieval
    └── Panel Context
    ↓
OpenRouter LLM
    ↓
Tool Execution
    ↓
Response Streaming
```

### AI Studio Workspace (V3.8)
```
Full-Screen AI Studio
    ↓
AdaptiveLayout (Three-Panel)
    ├── Left Panel - Conversation Sidebar
    │   ├── Conversation List
    │   ├── Create Conversation
    │   ├── Switch Conversations
    │   └── Delete Conversations
    ├── Center Panel - Chat Workspace
    │   ├── Message Timeline
    │   ├── Message Composer
    │   └── Message Display
    └── Right Panel - Project Intelligence
        ├── Overview (V3.11 - AI-generated)
        ├── Characters (V3.9 - real data)
        ├── Story (V3.9 - real data)
        ├── Relationships (V3.9 - real data)
        ├── Design Decisions (V3.9 - real data)
        ├── Art Style (V3.9 - real data)
        ├── Preferences (V3.9 - real data)
        ├── Panels (V3.10 - real data)
        ├── Locations (V3.9 - real data)
        ├── Notes (V3.9 - real data)
        └── Context (V3.9 - real data, V3.12 - AI tools)
```

**Project Intelligence Panel Architecture:**
- Configuration-based sections array (easy to extend)
- Reusable `IntelligenceSection` component for consistent UI
- Supports `actions` prop for edit/delete buttons
- Placeholder content in V3.8, real data in V3.9+
- Flexible for future features (world building, locations, themes, etc.)

### Data Flow for AI Requests (streaming, V3.11)
```
User types -> MessageComposer
    ↓ onSendMessage
ChatWorkspace.handleSendMessage
    ↓ conversationService.streamChatMessage (fetch, reads SSE)
    ├── event:start -> refresh list (user message appears)
    ├── event:token -> append to target buffer (typewriter reveal)
    ├── event:done  -> reply already saved; refresh and swap in saved message
    └── event:error -> show error, keep user message
```

### Data Flow for AI Requests (non-streaming, V3.11 M1)
```
User Message
    ↓
React Frontend
    ↓ (HTTP)
FastAPI Backend
    ↓
Authentication Check
    ↓
Context Builder
    ├── Load Conversation History
    ├── Retrieve Project Memory
    ├── RAG Vector Search
    └── Load Panel Context (if applicable)
    ↓
OpenRouter API Call
    ↓
Tool Execution (if tools called)
    ↓
Response Streaming
    ↓
React Frontend
```

### Image Generation Flow
```
User Request
    ↓
React Frontend
    ↓ (HTTP)
FastAPI Backend
    ↓
Image Generation Service
    ├── Load Reference Image
    ├── Encode to Base64
    └── OpenRouter Image API
    ↓
Base64 Response
    ↓
Decode and Save
    ↓
Object Storage
    ↓
Metadata to MongoDB
    ↓
React Frontend Display
```

### RAG Pipeline
```
Project Memory
    ↓
Embedding Generation
    ↓
Vector Embeddings (MongoDB)
    ↓
User Query
    ↓
Vector Search
    ↓
Relevant Context
    ↓
LLM Context Assembly
    ↓
Enhanced Response
```

## Implementation Status

### ✅ Implemented (V2)
- Gradio UI
- Python monolithic backend
- SQLite database
- Project management
- Conversation system
- Project memory
- Panel management
- Image generation (OpenRouter)
- Tool calling
- Multimodal panel analysis

### 🚧 Not Yet Implemented (V3)
- Panel management (V3.10)
- AI orchestration layer (V3.11)
- Tool calling system (V3.12)
- Multimodal panel analysis (V3.13)
- RAG/vector search (V3.14)
- Image generation abstraction (V3.15)
- Object storage (V3.16)
- Testing infrastructure (V3.17)
- Docker deployment (V3.18)
- Observability & monitoring (V3.19)
- Notification system (V3.20)

### ✅ Implemented (V3 - Foundation)
- FastAPI backend structure
- MongoDB connection (Motor + Beanie)
- Basic models (User, Project)
- Project CRUD API endpoints
- MongoDB Atlas integration
- React frontend structure
- React Router navigation
- TailwindCSS styling

### ✅ Implemented (V3 - Core Features)
- User authentication (JWT, bcrypt)
- Project ownership & authorization
- Conversation system (CRUD, pagination)
- Message system (CRUD, pagination)
- Project memory (12 types, CRUD, search)
- Project Intelligence panel (real memory data)
- AI Studio workspace (three-panel layout)
- React Router setup
- Layout components (Header, Sidebar)
- API client setup (Axios)
- TailwindCSS v4 styling
- Theme system (dark/light mode with persistence)
- Project CRUD UI (create, read, update, delete)
- Reusable components (Button, Modal, Loading)
- Project-specific components (ProjectCard, ProjectForm, DeleteProjectDialog)
- Form validation and error handling
- Responsive design with mobile drawer
- Lucide icons for professional UI
- Framer Motion for smooth animations
- Tutorial modal for new users
- Landing page with project description

## Planned Module Structure

```
mangacraft/
├── v2/                    # V2 (preserved during migration)
│   ├── app.py
│   ├── config.py
│   ├── llm.py
│   ├── prompts.py
│   ├── database/
│   ├── tools/
│   └── utils/
│
├── v3/                    # V3 (new development)
│   ├── frontend/         # React application
│   │   ├── src/
│   │   │   ├── components/
│   │   │   ├── pages/
│   │   │   ├── services/
│   │   │   └── App.tsx
│   │   ├── package.json
│   │   └── vite.config.js
│   │
│   ├── backend/          # FastAPI application
│   │   ├── main.py
│   │   ├── api/
│   │   │   ├── auth/
│   │   │   ├── projects/
│   │   │   ├── conversations/
│   │   │   ├── memories/
│   │   │   ├── panels/
│   │   │   └── ai/
│   │   ├── models/
│   │   │   ├── user.py
│   │   │   ├── project.py
│   │   │   ├── conversation.py
│   │   │   ├── message.py
│   │   │   ├── memory.py
│   │   │   └── panel.py
│   │   ├── services/
│   │   │   ├── ai_service.py
│   │   │   ├── context_builder.py
│   │   │   └── memory_service.py
│   │   ├── repositories/
│   │   │   ├── user_repository.py
│   │   │   ├── project_repository.py
│   │   │   └── memory_repository.py
│   │   └── config/
│   │
│   └── docker/
│       ├── Dockerfile.backend
│       ├── Dockerfile.frontend
│       └── docker-compose.yml
│
├── docs/                 # Documentation
│   ├── roadmap.md
│   ├── progress.md
│   ├── decisions.md
│   └── architecture.md
│
└── .env                 # Environment variables
```

## Key Design Principles

### Separation of Concerns
- Frontend handles UI and user interaction
- Backend handles business logic and data access
- Database handles persistence
- External services handle AI and storage

### Security Layers
- Authentication: Verify user identity
- Authorization: Verify user permissions
- Input validation: Validate all inputs
- Output sanitization: Sanitize all outputs

### Scalability Considerations
- Stateless backend for horizontal scaling
- Database indexing for query performance
- Vector search for efficient retrieval
- Object storage for file handling
- Caching strategy (if Redis introduced)

### Performance Considerations
- Async operations for I/O-bound tasks
- Database connection pooling
- Efficient vector search indexing
- Response streaming for AI interactions
- Lazy loading for large datasets

## Technology Justification

### Why React
- Modern, component-based UI
- Large ecosystem and community
- Aligns with MERN learning path
- Good for complex workflows

### Why FastAPI
- Native async/await support
- Automatic API documentation
- Type hints and validation
- Python-based (AI ecosystem)

### Why MongoDB
- Flexible schema for project data
- Built-in vector search
- Familiar to developer (MERN)
- Good for document-based data

### Why Lucide React
- Professional icon library
- Consistent, clean design
- Tree-shakeable (small bundle size)
- Easy to customize with CSS

### Why Framer Motion
- Smooth, professional animations
- Declarative API (React-like)
- Optimized for performance
- Better than CSS animations for complex interactions

### Why Theme System
- Dark/light mode for accessibility
- User preference persistence
- CSS variables for efficient theming
- No theme flash on initial load

### Why Motor (MongoDB Driver)
- Async driver designed for FastAPI
- Non-blocking database operations
- Better performance than PyMongo (sync driver)
- PyMongo would block FastAPI's async nature
- Motor is the async version of PyMongo

### Why Beanie (ODM)
- Pythonic MongoDB operations
- Similar to Mongoose in MERN
- Type hints and validation with Pydantic
- Makes MongoDB queries easy to write
- Async-compatible (works with Motor)

### Why OpenRouter
- Unified AI provider
- Multiple model access
- Single API key
- Good model selection

### Why Docker
- Consistent environments
- Easy deployment
- Industry standard
- Good for learning

## Notes

- This architecture will evolve as V3 is implemented
- Not all components are final - decisions may change based on implementation experience
- Documentation will be updated as architecture materializes
- Planned architecture should be treated as direction, not rigid requirement