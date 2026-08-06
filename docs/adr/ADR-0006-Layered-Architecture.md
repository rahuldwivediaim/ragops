# ADR-0006: Layered Architecture

## Status

Accepted

## Context

As the RAGOps platform grows, maintaining a clear dependency structure is essential to avoid circular dependencies, improve testability, and simplify maintenance.

## Decision

The platform follows a layered architecture.

The `common` package forms the foundation of the system and must not depend on any other internal project modules.

Dependencies are one-directional.

```
API
 ↓
Services
 ↓
Providers
 ↓
Storage
 ↓
Config
 ↓
Common
```

Higher layers may depend on lower layers, but lower layers must never depend on higher layers.

## Consequences

- No circular imports
- Better modularity
- Easier unit testing
- Cleaner architecture
- Independent reusable common library
