# MangaCraft V3 Architectural Decisions

## Decision Records

This document records important architectural and design decisions made during MangaCraft V3 development.

---

## Technology Stack Decisions

### Why FastAPI was selected
**Date**: TBD
**Context**: Backend framework selection for V3
**Decision**: Use FastAPI instead of Flask or Django
**Rationale**:
- Native async/await support for better performance
- Automatic OpenAPI documentation generation
- Type hints with Pydantic for validation
- Python-based (aligns with AI ecosystem)
- Modern and actively maintained
**Alternatives Considered**: Flask (simpler but less modern), Django (too heavy for API-focused backend)
**Trade-offs**: FastAPI learning curve, but acceptable given Python knowledge

### Why MongoDB was selected
**Date**: TBD
**Context**: Database selection for V3
**Decision**: Use MongoDB instead of PostgreSQL
**Rationale**:
- Developer already familiar with MongoDB from MERN learning
- Natural fit with MERN ecosystem
- Flexible schema for project data
- Built-in support for vector search (Atlas Vector Search)
- Reduces learning overhead
**Alternatives Considered**: PostgreSQL (more traditional but unfamiliar to developer)
**Trade-offs**: Less strict schema enforcement, but acceptable for document-based project data

### Why MongoDB Atlas Vector Search was selected
**Date**: TBD
**Context**: Vector search technology for RAG implementation
**Decision**: Use MongoDB Atlas Vector Search instead of dedicated vector database
**Rationale**:
- Single database for both structured data and vectors
- Reduces infrastructure complexity
- Familiar MongoDB interface
- Cost-effective for current scale
**Alternatives Considered**: Pinecone, Qdrant, Weaviate (dedicated vector databases)
**Trade-offs**: May need dedicated vector DB at scale, but can migrate later if needed

### Why React with Vite was selected
**Date**: TBD
**Context**: Frontend framework selection for V3
**Decision**: Use React with Vite instead of Gradio
**Rationale**:
- Modern, production-ready web framework
- Aligns with MERN learning path
- Vite provides fast development experience
- Large ecosystem and community support
- Better than Gradio for complex workflows
**Alternatives Considered**: Next.js (more complex for initial migration), Vue.js (less familiar)
**Trade-offs**: More complex initial setup than Gradio, but necessary for production application

### Why OpenRouter was selected for AI
**Date**: September 2026 (Image Generation), TBD (LLM)
**Context**: AI provider selection
**Decision**: Use OpenRouter for both LLM and image generation
**Rationale**:
- Single API key for multiple AI services
- Access to multiple models and providers
- Unified billing and management
- Good model selection (Gemini, GPT, etc.)
- Already used in V2 for LLM
**Alternatives Considered**: Direct Google API, Direct OpenAI API, Hugging Face (removed)
**Trade-offs**: Vendor lock-in, but acceptable given provider reliability

### Why OpenRouter Image API was selected
**Date**: September 2026
**Context**: Image generation provider migration
**Decision**: Migrate from Hugging Face to OpenRouter Image API
**Rationale**:
- Unified billing with LLM usage
- Single API key management
- Better model selection (Gemini 2.5 Flash Image)
- Supports image-to-image via input_references
- Already integrated with existing OPENROUTER_API_KEY
**Alternatives Considered**: Keep Hugging Face, Direct Google Image API
**Trade-offs**: Different API structure, but successfully migrated

## Architecture Decisions

### Authentication Approach
**Date**: TBD
**Context**: User authentication and session management
**Decision**: JWT access tokens with refresh tokens
**Rationale**:
- Stateless authentication suitable for API
- Industry-standard approach
- Good security with token expiration
- Refresh tokens provide good UX without compromising security
**Alternatives Considered**: Session-based authentication (requires server-side state), OAuth (more complex)
**Trade-offs**: Token management complexity, but acceptable security trade-off

### Project Ownership Model
**Date**: TBD
**Context**: Multi-user project access control
**Decision**: User owns projects, authorization enforced at backend
**Rationale**:
- Clear data isolation between users
- Backend enforcement is more secure than frontend-only
- Simple and effective for current scale
- Easy to understand and maintain
**Alternatives Considered**: Team-based ownership (RBAC), shared projects (more complex)
**Trade-offs**: Less flexible than team model, but sufficient for individual use

### Conversation Limits
**Date**: TBD
**Context**: Managing conversation context and token usage
**Decision**: Maintain 25-turn limit from V2
**Rationale**:
- Proven effective in V2
- Controls token usage and costs
- Encourages focused conversations
- Easy to understand for users
**Alternatives Considered**: Unlimited with summarization, token-based limits
**Trade-offs**: Less flexible, but provides clear boundaries

### Memory Architecture
**Date**: TBD
**Context**: Project memory storage and retrieval
**Decision**: Structured memory types with RAG enhancement
**Rationale**:
- Combines structured storage with semantic search
- Preserves V2 memory types (character, story, relationship, etc.)
- RAG provides better retrieval than keyword search
- Flexible for future expansion
**Alternatives Considered**: Pure structured storage, pure vector search
**Trade-offs**: More complex than pure structured, but provides better UX

### Storage Architecture
**Date**: TBD
**Context**: File storage for panels and generated references
**Decision**: MongoDB for metadata, object storage for files
**Rationale**:
- Separation of concerns (metadata vs files)
- Scalable file storage
- Better for production deployment
- CDN capability
**Alternatives Considered**: Store files in MongoDB (not scalable), local filesystem only (not production-ready)
**Trade-offs**: More complex infrastructure, but necessary for production

### Testing Strategy
**Date**: TBD
**Context**: Quality assurance for V3
**Decision**: Unit tests + integration tests, manual testing for critical paths
**Rationale**:
- Balanced approach for learning project
- Unit tests for business logic
- Integration tests for key workflows
- Manual testing for UI/UX
**Alternatives Considered**: Full TDD (too time-consuming), no tests (risky)
**Trade-offs**: Less comprehensive than full test suite, but acceptable for learning project

### Deployment Decisions
**Date**: TBD
**Context**: Production deployment infrastructure
**Decision**: Docker containers with docker-compose for local development
**Rationale**:
- Consistent environments
- Easy local development setup
- Production-ready containerization
- Industry-standard approach
**Alternatives Considered**: Manual deployment (error-prone), Kubernetes (overkill for current scale)
**Trade-offs**: Docker learning curve, but valuable skill

## Design Decisions

### Project Data Model
**Date**: TBD
**Context**: How projects and related data are structured
**Decision**: User → Projects → (Conversations, Panels, Memories, References)
**Rationale**:
- Clear ownership hierarchy
- Natural extension of V2 structure
- Easy to understand and query
- Supports future multi-user scenarios
**Alternatives Considered**: Flat structure, team-based structure
**Trade-offs**: Less flexible than team model, but simpler and sufficient

### Tool Calling Architecture
**Date**: TBD
**Context**: How AI tools are organized and executed
**Decision**: Centralized tool registry with authorization checks
**Rationale**:
- Consistent tool management
- Security through authorization
- Easy to add new tools
- Clear separation from business logic
**Alternatives Considered**: Distributed tool definitions, inline tool logic
**Trade-offs**: More structured than inline, but more maintainable

### Error Handling Strategy
**Date**: TBD
**Context**: How errors are handled across the application
**Decision**: Structured error responses with user-friendly messages
**Rationale**:
- Better UX than raw errors
- Easier debugging with logging
- Consistent error format
- Security (no sensitive data in errors)
**Alternatives Considered**: Raw exceptions, silent failures
**Trade-offs**: More code than raw exceptions, but much better UX

---

## Future Decisions

These decisions will be made when the relevant phase is implemented:

- RAG implementation details (chunking strategy, embedding model)
- Vector search configuration (indexing, similarity thresholds)
- Image generation provider abstraction details
- Rate limiting strategy
- Caching strategy (if Redis is introduced)
- Background job processing (if needed)
- Monitoring and logging implementation details
