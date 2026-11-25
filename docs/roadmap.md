# MangaCraft V3 Roadmap

## Overview

MangaCraft V3 transforms the V2 Gradio prototype into a full-stack application with React, FastAPI, MongoDB, authentication, and AI capabilities.

## Technology Stack

- **Frontend**: React
- **Backend**: FastAPI
- **Database**: MongoDB
- **AI**: OpenRouter (LLM + Image Generation)
- **Storage**: Object Storage (S3-compatible)

## 20-Phase Roadmap

### Milestone 1: Foundation (V3.1–V3.5)

#### V3.1: Project Structure & Environment Setup
- [x] Completed
- **Goal**: Establish the foundational project structure for V3 while keeping V2 operational
- **Technologies**: Python virtual environment, Node.js environment, directory structure
- **What is Implemented**: Separate V2/V3 directory structure, environment configuration, documentation structure
- **V2 Functionality Preserved**: All V2 functionality remains fully operational
- **Tests/Success Criteria**: V2 still runs, V3 directory structure created, environment setup tested
- **Must Complete Before V3.2**: V3 directory structure approved, environment setup tested, V2 confirmed working

#### V3.2: FastAPI Backend Foundation
- [x] Completed
- **Goal**: Create the FastAPI backend skeleton with basic routing and structure
- **Technologies**: FastAPI, Pydantic, CORS middleware
- **What is Implemented**: FastAPI application, basic API router structure, health check endpoint, error handling
- **V2 Functionality Preserved**: V2 still fully operational
- **Tests/Success Criteria**: FastAPI server starts, health check returns 200, Swagger UI accessible
- **Must Complete Before V3.3**: FastAPI server runs locally, API documentation verified
- **Completion Date**: 2026-11-13

#### V3.3: MongoDB Integration & Basic Models
- [x] Completed
- **Goal**: Establish MongoDB connection and implement basic data models
- **Technologies**: MongoDB, Motor (async driver), Beanie ODM
- **What is Implemented**: MongoDB connection, Beanie models, User/Project models, indexing
- **V2 Functionality Preserved**: V2 SQLite database unchanged
- **Tests/Success Criteria**: MongoDB connection successful, Project model CRUD tested
- **Must Complete Before V3.4**: MongoDB running locally, Project model defined, CRUD operations tested
- **Completion Date**: 2026-11-13
- **Note**: Using MongoDB Atlas (cloud) instead of local MongoDB for development

#### V3.4: React Frontend Foundation
- [x] Completed
- **Goal**: Create the React application skeleton with basic routing and structure
- **Technologies**: React (Vite), React Router, Axios, TailwindCSS v4
- **What is Implemented**: React app, basic routing, layout components, API client setup, TailwindCSS styling
- **V2 Functionality Preserved**: V2 Gradio UI still fully operational
- **Tests/Success Criteria**: React app builds, routing works, can call FastAPI health endpoint
- **Must Complete Before V3.5**: React app runs locally, can call FastAPI endpoints, routing tested
- **Completion Date**: 2026-11-13

#### V3.5: Basic Project CRUD
- [x] Completed
- **Goal**: Implement project management in V3, preserving V2 project functionality
- **Technologies**: FastAPI endpoints, React UI, MongoDB repositories, ThemeContext, Lucide icons, Framer Motion
- **What is Implemented**: Project CRUD endpoints, React project management UI, theme system, responsive design, tutorial modal
- **V2 Functionality Preserved/Migrated**: V2 projects remain in SQLite, V3 projects in MongoDB (dual system)
- **Tests/Success Criteria**: Can create/list/edit/delete projects, projects persist in MongoDB, theme toggle works, responsive design works
- **Must Complete Before V3.6**: All CRUD operations tested, UI validates inputs, error handling works
- **Completion Date**: 2026-11-15

### Milestone 2: Core Features (V3.6–V3.10)

#### V3.6: Authentication & User System
- [x] Completed
- **Goal**: Implement user authentication with registration, login, and session management
- **Technologies**: User model, bcrypt, JWT tokens, authentication middleware, AuthContext
- **What is Implemented**: User registration/login endpoints, JWT tokens, auth dependency, login/registration UI, protected routes, logout functionality
- **V2 Functionality Preserved**: V2 remains single-user (no auth needed)
- **Tests/Success Criteria**: Can register/login, tokens expire, protected routes reject unauthenticated requests, users can only see their own projects
- **Must Complete Before V3.7**: Registration flow tested, login flow tested, token refresh tested
- **Completion Date**: 2026-11-16

#### V3.7: Project Ownership & Authorization
- [x] Completed
- **Goal**: Enforce project ownership so users can only access their own projects
- **Technologies**: Project ownership, authorization middleware, user-project relationships
- **What is Implemented**: Project ownership checks, project list filtering (cascade delete deferred to user management phase)
- **V2 Functionality Preserved**: V2 remains single-user (no ownership needed)
- **Tests/Success Criteria**: User A cannot see/access User B's projects, unauthorized requests return 403
- **Must Complete Before V3.8**: Ownership checks tested, authorization middleware verified
- **Completion Date**: 2026-11-16
- **Note**: Implemented as part of V3.6 authentication system. Cascade delete deferred to future user management phase.

#### V3.8: Conversation System Migration
- [x] Completed
- **Goal**: Migrate V2 conversation functionality to V3 with proper multi-user support
- **Technologies**: Conversation model, Message model, Conversation/Message repositories
- **What is Implemented**: Conversation CRUD endpoints, conversation switching UI, offset-based pagination, cascade deletion, full-screen AI Studio workspace, three-panel adaptive layout
- **V2 Functionality Preserved/Migrated**: V2 conversations remain in SQLite, V3 can import V2 conversations
- **Tests/Success Criteria**: Can create/list conversations, conversation history persists, message pagination works, cascade deletion verified
- **Must Complete Before V3.9**: Conversation CRUD tested, message persistence tested, pagination verified
- **Completion Date**: 2026-11-16

#### V3.9: Project Memory Migration
- [x] Completed
- **Goal**: Migrate V2 project memory system to V3 with proper indexing and search
- **Technologies**: ProjectMemory model, Memory repository, search endpoint
- **What is Implemented**: Memory CRUD endpoints, memory search UI, project context view, all 12 V2 memory types + V3 additions, Project Intelligence integration with real memory data
- **V2 Functionality Preserved/Migrated**: V2 memory types preserved, V2 search preserved, V3 can import V2 memories
- **Tests/Success Criteria**: Can save/retrieve memories, search works, duplicate detection works, memory type filtering works, Project Intelligence shows real data
- **Must Complete Before V3.10**: Memory CRUD tested, search functionality tested, context retrieval tested
- **Completion Date**: 2026-11-19

#### V3.10: Panel Management Migration
- [x] Completed
- **Goal**: Migrate V2 panel upload and management to V3 with proper file handling
- **Technologies**: Panel model, Beanie ODM, file upload handling, local file storage, Pillow (image dimensions), file validation
- **What is Implemented**: Panel upload/list/get/patch/delete endpoints, AI Studio panel gallery (grid/storyboard/list views), drag & drop multi-file upload, file validation (size, type, dimensions), scene notes persistence, cascade deletion
- **V2 Functionality Preserved/Migrated**: V2 panel upload preserved, V3 stores panels locally under `panels/{project_id}/`
- **Tests/Success Criteria**: Can upload/list/get/delete panels, files stored correctly, file validation works (size/type/dimension), invalid files rejected, notes persist
- **Must Complete Before V3.11**: Panel upload tested, panel display tested, file validation verified
- **Completion Date**: 2026-11-25

### Milestone 3: AI & Intelligence (V3.11–V3.15)

#### V3.11: AI Orchestration Layer
- [ ] Not Started
- **Goal**: Create the AI orchestration service that manages LLM interactions, context building, and tool routing
- **Technologies**: AI service layer, Context builder, LLM client abstraction, OpenRouter integration
- **What is Implemented**: AI service, context builder, chat endpoint, streaming response, rate limiting
- **V2 Functionality Preserved**: V2 AI interactions still work, V2 tool calling still works
- **Tests/Success Criteria**: Can send message to AI, AI responds with streaming, context includes history
- **Must Complete Before V3.12**: AI service tested, streaming verified, context builder tested

#### V3.12: Tool Calling System Migration
- [ ] Not Started
- **Goal**: Migrate V2 tool calling system to V3 with proper structure and integration
- **Technologies**: Tool registry, Tool executor, Tool schemas, Project memory tools, Panel tools
- **What is Implemented**: Tool registry, tool executor, memory tools, panel tools, tool authorization
- **V2 Functionality Preserved/Migrated**: V2 tool calling concept preserved, V2 tool schemas preserved
- **Tests/Success Criteria**: AI can call tools, tools execute correctly, project memory tools work
- **Must Complete Before V3.13**: Tool registry tested, tool executor verified, memory tools tested

#### V3.13: Multimodal Panel Analysis
- [ ] Not Started
- **Goal**: Implement AI-powered panel analysis and composition analysis in V3
- **Technologies**: Vision model integration, Panel analysis tool, Composition analysis tool
- **What is Implemented**: Panel analysis tool, composition analysis tool, image encoding, visual intent detection
- **V2 Functionality Preserved/Migrated**: V2 panel analysis preserved, V2 composition analysis preserved
- **Tests/Success Criteria**: Can analyze selected panel, can analyze composition, vision model works
- **Must Complete Before V3.14**: Panel analysis tested, composition analysis tested, multimodal handling verified

#### V3.14: RAG & Vector Search
- [ ] Not Started
- **Goal**: Implement RAG (Retrieval-Augmented Generation) with vector search for semantic memory retrieval
- **Technologies**: Embedding generation, Vector embeddings storage, Vector search, RAG context builder
- **What is Implemented**: Embedding service, vector embeddings in MongoDB, vector search endpoint, RAG context builder
- **V2 Functionality Preserved/Enhanced**: V2 memory search enhanced (now semantic), V2 project context enhanced
- **Tests/Success Criteria**: Can generate embeddings, vector search returns relevant results, RAG context builder works
- **Must Complete Before V3.15**: Embedding service tested, vector search verified, RAG context builder tested

#### V3.15: Image Generation Abstraction
- [ ] Not Started
- **Goal**: Create provider abstraction for image generation, preserving Hugging Face and enabling future providers
- **Technologies**: Image generation provider interface, Hugging Face provider, OpenRouter provider
- **What is Implemented**: Provider interface, Hugging Face provider, Image generation service, Reference CRUD
- **V2 Functionality Preserved/Migrated**: V2 Hugging Face integration preserved, V3 can import V2 references
- **Tests/Success Criteria**: Can generate reference via Hugging Face, provider abstraction works, references persist
- **Must Complete Before V3.16**: Provider abstraction tested, Hugging Face provider tested, Reference CRUD tested

### Milestone 4: Production Readiness (V3.16–V3.20)

#### V3.16: Object Storage Integration
- [ ] Not Started
- **Goal**: Replace local file storage with object storage (S3-compatible) for panels and references
- **Technologies**: Object storage abstraction, S3-compatible storage (MinIO local, AWS S3 production)
- **What is Implemented**: Object storage provider interface, MinIO provider, AWS S3 provider, Storage service
- **V2 Functionality Preserved**: V2 still uses local storage
- **Tests/Success Criteria**: Can upload to object storage, can retrieve via presigned URLs, MinIO works locally
- **Must Complete Before V3.17**: Object storage tested locally, S3 configuration tested, upload/download verified

#### V3.17: Testing Infrastructure
- [ ] Not Started
- **Goal**: Implement comprehensive testing for backend, frontend, and integration
- **Technologies**: Pytest, React Testing Library, integration tests, test fixtures
- **What is Implemented**: Backend unit tests, frontend component tests, integration tests, coverage reporting
- **V2 Functionality Preserved**: V2 test files preserved, V2 tests still runnable
- **Tests/Success Criteria**: Backend tests pass (80%+ coverage), frontend tests pass, integration tests pass
- **Must Complete Before V3.18**: Test suite passes, coverage acceptable, V2 tests still pass

#### V3.18: Docker & Deployment
- [ ] Not Started
- **Goal**: Containerize the application and create deployment configuration
- **Technologies**: Docker containers, Docker Compose, multi-stage builds, environment-based configuration
- **What is Implemented**: Backend Dockerfile, Frontend Dockerfile, Docker Compose, production configuration
- **V2 Functionality Preserved**: V2 can still run locally without Docker
- **Tests/Success Criteria**: Can run entire stack with Docker Compose, all services start correctly
- **Must Complete Before V3.19**: Docker Compose tested locally, production configuration tested, backup strategy verified

#### V3.19: Observability & Monitoring
- [ ] Not Started
- **Goal**: Implement logging, monitoring, and error tracking for production operations
- **Technologies**: Structured logging, Request ID tracking, Error tracking, Performance monitoring, Caching layer
- **What is Implemented**: Structured logging, request ID middleware, error tracking integration, API latency logging, Redis caching for memory/context loads
- **V2 Functionality Preserved**: V2 logging unchanged
- **Tests/Success Criteria**: Structured logs generated, request IDs tracked, errors captured in error tracking, cache hits improve performance
- **Must Complete Before V3.20**: Logging configured, error tracking tested, metrics verified, caching tested

#### V3.20: V2 Deprecation & Handover
- [ ] Not Started
- **Goal**: Finalize V3, deprecate V2, and complete the migration
- **Technologies**: Final migration scripts, V2 deprecation notice, Documentation updates, Notification system, Email service
- **What is Implemented**: Final migration scripts, V2 archival, migration guide, complete documentation, notification system for AI task completion, email service for account recovery
- **V2 Functionality Preserved**: V2 archived and preserved, V2 can still be run if needed
- **Tests/Success Criteria**: All V2 data migrates successfully, V3 fully functional without V2, documentation complete, notifications trigger correctly, emails send successfully
- **Must Complete (Final Phase)**: Migration scripts tested, all V2 functionality verified in V3, documentation complete, notification system tested, email service verified

## Migration Strategy

### V2 to V3 Data Migration
- Projects: SQLite → MongoDB
- Conversations: SQLite → MongoDB
- Messages: SQLite → MongoDB
- Project Memory: SQLite → MongoDB
- Panels: SQLite → MongoDB + local file storage
- Generated References: SQLite → MongoDB + local file storage

### V2 Preservation
- V2 remains operational during V3 development
- V2 can be used as fallback during migration
- V2 archived to `/v2-archived` after V3 completion
