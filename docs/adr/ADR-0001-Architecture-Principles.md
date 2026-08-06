# ADR-0001: Core Architecture Principles

| Property | Value |
|----------|-------|
| ADR Number | ADR-0001 |
| Title | Core Architecture Principles |
| Status | Accepted |
| Date | 28 July 2026 |
| Author | Rahul Dwivedi |

---

# Context

RAGOps is intended to become an enterprise-grade AI Knowledge Platform rather than a project-specific RAG implementation.

Traditional RAG solutions often evolve into tightly coupled systems where business logic depends directly on specific AI providers, vector databases, or cloud platforms. Such designs reduce portability, increase maintenance costs, and make future enhancements difficult.

To ensure long-term maintainability, scalability, and extensibility, a set of architectural principles is required before implementation begins.

---

# Decision

RAGOps adopts the following architectural principles.

## 1. Provider Agnostic

No business component shall depend directly on a specific provider implementation.

All provider integrations must implement common interfaces.

Examples include:

- OpenAI
- Azure OpenAI
- Anthropic
- Google Gemini
- Ollama
- AWS Bedrock

The business layer must remain independent of these providers.

---

## 2. Plugin-Based Architecture

External capabilities shall be implemented as plugins.

Supported plugin categories include:

- LLM Providers
- Embedding Providers
- Vector Stores
- OCR Engines
- Storage Providers
- Authentication Providers
- Notification Providers

The framework core must never require modification when a new provider is introduced.

---

## 3. Configuration-Driven Platform

Application behaviour must be controlled through configuration rather than code wherever possible.

Configuration includes:

- Provider selection
- Model selection
- Chunking strategies
- Embedding strategies
- Retrieval strategies
- Security settings
- Deployment configuration

---

## 4. Layered Architecture

The platform is organised into logical layers.

Applications

↓

SDK / REST API

↓

Control Plane

↓

Knowledge Plane

↓

Retrieval Plane

↓

Operations Plane

↓

Provider Layer

↓

Infrastructure

Each layer has a clearly defined responsibility.

---

## 5. Separation of Concerns

Business logic must remain independent from infrastructure.

Infrastructure services must never contain business rules.

Provider plugins must never contain workflow orchestration.

---

## 6. API-First Design

Every major capability shall be exposed through REST APIs.

The Web UI, SDK, and external applications shall consume the same APIs.

---

## 7. SDK-First Development

Every REST capability shall have an equivalent SDK implementation.

Developers should be able to integrate RAGOps without directly invoking REST APIs.

---

## 8. Security by Design

Security is considered a foundational architectural concern.

Every module shall support:

- Authentication
- Authorization
- RBAC
- Audit Logging
- Secure Configuration
- Secret Management

---

## 9. Observability by Default

Every platform component shall expose operational metrics.

Examples include:

- Health Status
- Processing Metrics
- Performance Metrics
- Error Rates
- Audit Events

---

## 10. Enterprise First

Architectural decisions shall prioritise enterprise use cases including:

- Multi-workspace support
- High availability
- Governance
- Compliance
- Extensibility
- Operational excellence

---

# Consequences

## Advantages

- High extensibility
- Easier maintenance
- Simplified provider replacement
- Better scalability
- Improved testability
- Enterprise readiness
- Reduced vendor lock-in

---

## Trade-offs

- Additional abstraction layers
- More interfaces to maintain
- Slightly increased implementation complexity
- Longer initial development time

These trade-offs are accepted because they significantly improve long-term maintainability.

---

# Related Documents

- Product Requirements Document
- Software Architecture
- High Level Design
- Plugin Architecture
- Configuration Framework

---

# Status

Accepted

## Strong Typing Strategy

To improve maintainability and reduce programming errors, the platform uses strong typing throughout the codebase.

The `common.types` module provides reusable domain-specific type aliases using Python's `typing.NewType` where appropriate.

Examples include:

- RequestId
- CorrelationId
- TraceId
- DocumentId
- ChunkId
- VectorId
- UserId
- TenantId

Using semantic types improves readability, enables stronger static type checking, and makes the intent of APIs clearer while introducing no runtime overhead.

Generic aliases for JSON structures and embedding vectors are also centralized in `common.types` to eliminate duplicated type definitions across the project.

## Platform Identifier Strategy

All platform resources use semantically meaningful identifiers.

Identifiers consist of a resource-specific prefix followed by a globally unique identifier.

Examples:

- doc_<uuid>
- chunk_<uuid>
- vec_<uuid>
- req_<uuid>
- corr_<uuid>
- usr_<uuid>

Benefits include:

- Easier debugging
- Improved log readability
- Simpler troubleshooting
- Clear resource identification
- Consistent identifier generation across all modules

Identifier generation is centralized within the `common.uuid` module to ensure consistency and avoid duplicated logic.

## Shared Type System

The platform defines a centralized type system in `backend.common.types`.

This module provides:

- Semantic identifier types
- Generic JSON type aliases
- Metadata types
- Embedding vector types
- Shared protocols
- Generic callable signatures

Using a centralized type system ensures consistency, improves readability, enhances static analysis, and reduces duplicated type definitions across the codebase.

The `common.types` module serves as the canonical source for shared domain-neutral types and should be preferred over ad-hoc type aliases within individual modules.
