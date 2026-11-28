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

### Why Motor was selected instead of PyMongo
**Date**: 2026-11-13
**Context**: MongoDB driver selection for FastAPI
**Decision**: Use Motor (async driver) instead of PyMongo (sync driver)
**Rationale**:
- FastAPI is an async framework (built on async/await)
- Motor is the async version of PyMongo, designed for async frameworks
- PyMongo is synchronous and would block the entire application
- Motor allows non-blocking database operations for better performance
- Multiple requests can be handled simultaneously without blocking
- PyMongo is better for sync frameworks like Flask/Django
**Alternatives Considered**: PyMongo (synchronous, blocks FastAPI)
**Trade-offs**: Motor has slightly different API than PyMongo, but necessary for FastAPI performance

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
**Date**: 2026-11-19
**Context**: Project memory storage and retrieval
**Decision**: Structured memory types with RAG enhancement
**Rationale**:
- Combines structured storage with semantic search
- Preserves V2 memory types (character, story, relationship, design_decision, art_style, preference, panel, generated_reference, character_reference, other_asset)
- Added V3-specific types (location, note) for flexibility
- RAG provides better retrieval than keyword search (V3.14)
- Flexible for future expansion
**Alternatives Considered**: Pure structured storage, pure vector search
**Trade-offs**: More complex than pure structured, but provides better UX
**Implementation Notes**:
- 12 memory types total (10 from V2 + 2 V3 additions)
- MongoDB with indexes on project_id, user_id, type, tags
- Regex-based search now, vector search in V3.14
- Project Intelligence panel shows real memory data with limits
- Libraries.dev animations for UI polish (BorderBeam, ThinkingOrb, MetalFx)

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

## AI Orchestration Decisions (V3.11)

### Why Server-Sent Events (SSE) for chat streaming
**Date**: 2026-11-26
**Context**: V3.11 M2 needed to stream AI replies token-by-token
**Decision**: Use Server-Sent Events (`text/event-stream`) via FastAPI `StreamingResponse`
**Rationale**:
- One-way server-to-client stream fits chat perfectly
- Works over plain HTTP (no WebSocket handshake or extra state)
- The browser reads it with a plain `fetch` + `ReadableStream` reader
- Simple, beginner-friendly, and easy to debug (each event is a `data:` line)
**Alternatives Considered**: WebSockets (bidirectional, heavier than needed), polling (wasteful, not live)
**Trade-offs**: One-way only; fine because the client sends the request up front

### Why a client-side typewriter reveal was added
**Date**: 2026-11-26
**Context**: Fast models return short replies in one network chunk, so tokens were batched into a single React paint and streaming looked invisible
**Decision**: Keep a `target` buffer (received text) and a `displayed` buffer (shown text); reveal a few characters per frame until they match
**Rationale**:
- Makes streaming visible even when the whole reply arrives instantly
- Does NOT slow the server or the model; only paces the reveal in the browser
- Produces the familiar ChatGPT-style typing effect
**Alternatives Considered**: Artificial server delay (dishonest, wastes time), no reveal (streaming invisible on fast replies)
**Trade-offs**: Slight added frontend complexity; tuned to stay snappy (~15 frames to catch up)

### Why panel/image analysis is deferred to V3.12–V3.13
**Date**: 2026-11-26
**Context**: Asking the AI to "analyze the panel" fails: the AI only receives panel metadata, not the image
**Decision**: Do not attempt image analysis in V3.11
**Rationale**:
- `context_builder` sends filename, dimensions, and notes only (no pixels)
- Panel analysis needs a tool the AI can call (V3.12 Tool Calling System Migration) and vision input (V3.13 Multimodal Panel Analysis)
- Doing it now would require passing image bytes into the prompt without tool/vision support
**Alternatives Considered**: Inline base64 images in the prompt now (premature; no tool or vision workflow)
**Trade-offs**: Until V3.12–V3.13, the AI can only reason about panels it is told about in text

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

## Product Direction Decisions (V4 and beyond)

### Chosen product direction: Creator-focused
**Date**: 2026-11-28
**Context**: Two long-term visions were considered - (A) a learning + creation platform, and (B) a creator-focused production platform.
**Decision**: Commit to Option B, the creator-focused platform.
**Rationale**:
- Continues directly from V2/V3 (projects, conversations, tool calling, project memory, panels, references)
- Matches the existing V3 roadmap (tool calling -> multimodal -> RAG -> image generation)
- Its promises are testable; A's hardest promises (adaptive skill tracking, artwork critiquing) are easy to fake and hard to do well
- Beginners are still supported through project-aware Q&A and AI image generation, without building a learning platform
**Alternatives Considered**: Option A (learning + creation), a creator-first hybrid
**Trade-offs**: MangaCraft will not teach drawing fundamentals through structured lessons

### Version relationship model: cumulative milestones
**Date**: 2026-11-28
**Context**: Should later versions replace earlier ones after deployment?
**Decision**: Treat versions as cumulative milestones of a single, continuously deployed application.
**Rationale**:
- V4 requires V3 (auth, projects, AI orchestration, memory); V5 requires V4. Each builds on the last.
- One deployment; every push to the main branch reflects the new features.
- Nothing is erased: a later version contains all earlier functionality.
**Alternatives Considered**: Separate apps per version (duplication, fragmentation)
**Implementation Notes**:
- Git: `main` stays deployable; use feature branches per phase; tag releases (e.g. `v3.0.0`) for snapshots.

### Collaboration: kept but best-effort
**Date**: 2026-11-28
**Context**: Should collaboration (V6) be a core goal?
**Decision**: Keep collaboration as a desirable, best-effort capability - not an essential pillar.
**Rationale**:
- MangaCraft will be deployed, so visitors may want to collaborate
- But real-time editing introduces a new discipline (WebSockets, Yjs/CRDT) that is premature without real users
- Cheap, useful pieces (permissions, activity/version history) can come earlier; heavy live-edit tooling only when needed
**Alternatives Considered**: Drop collaboration entirely, or make it a core pillar
**Trade-offs**: Live collaborative editing is deferred until a concrete need appears

### AI cost protection & deployment access model
**Date**: 2026-11-28
**Context**: The app uses a single OpenRouter API key, so every user's chat spends the owner's balance. A public deployment with open registration and no limits would be drained (including by scripted abuse).
**Decision**: Deploy privately first; before allowing other users, require login and enforce per-user AI limits. Treat BYOK (bring-your-own-key) as the option for fully open access.
**Rationale**:
- The single key cannot distinguish users; whoever chats, the owner pays.
- The most expensive part is the re-sent project briefing + last 20 messages on every turn; the history cap is already the main cost lever.
- Per-user caps (rate limiting, V3.19) turn unpredictable cost into bounded cost.
- BYOK shifts cost to the user and removes drain risk for open access.
**Alternatives Considered**: Open registration with owner-paid key (rejected: drain risk); subscriptions (deferred to V8)
**Trade-offs**: Limits reduce convenience; BYOK adds user friction

---

## Future Decisions

These decisions will be made when the relevant phase is implemented:

- V4+ Manga Intelligence details (character/relationship/story models, continuity approach)
- Whether a graph database (e.g. Neo4j) is ever justified over MongoDB relationships
- RAG implementation details (chunking strategy, embedding model)
- Vector search configuration (indexing, similarity thresholds)
- Image generation provider abstraction details
- Rate limiting strategy
- Caching strategy (if Redis is introduced)
- Background job processing (if needed)
- Monitoring and logging implementation details
