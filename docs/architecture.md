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
React Login Page
    ↓ (POST /api/auth/login)
FastAPI Auth Service
    ↓ (JWT generation)
Token Storage (httpOnly cookies)
    ↓ (token in Authorization header)
Protected Routes
```

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

### AI Orchestration
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

### Data Flow for AI Requests
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
- React frontend
- FastAPI backend
- MongoDB database
- User authentication
- Project ownership
- AI orchestration layer
- RAG/vector search
- Object storage
- Docker deployment
- Testing infrastructure

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