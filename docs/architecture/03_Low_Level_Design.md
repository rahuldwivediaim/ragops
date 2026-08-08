
# Low Level Design (LLD)

| Property | Value |
|----------|-------|
| Product | RAGOps |
| Version | 1.1.0 |
| Status | Approved |
| Last Updated | August 2026 |

# Low Level Design (Expanded)

## Dependency Rules
- `common` may be imported by all modules.
- Feature modules communicate through public service interfaces.
- No circular dependencies.
- Business services must not access provider implementations directly.
- External technologies must be accessed through provider abstractions.
- Parsers must be created through the ParserFactory.
- Providers must implement their respective base interfaces.

## Request Lifecycle
1. HTTP Request
2. FastAPI Router
3. Request Validation
4. Application Service
5. Business Validation
6. Repository
7. Processing Pipeline (if applicable)
8. Parser Framework
9. Provider Framework
10. Response Mapping
11. Operation Tracking
12. HTTP Response

## Transaction Boundaries
Transactions are owned by the service layer. Repository methods must not begin or commit transactions.
Processing activities should execute outside database transaction boundaries wherever practical.

## Testing Strategy
- Unit tests
- Repository integration tests
- Parser unit tests
- Provider unit tests
- API integration tests
- End-to-end document ingestion tests

## Service Responsibilities

- Routers expose REST endpoints.
- Services orchestrate business operations.
- Repositories handle persistence.
- ParserFactory selects parsers.
- Parsers coordinate document parsing.
- Providers integrate external libraries and services.
- OperationTracker records operational events.

## Processing Pipeline

Current implementation:

Upload
→ Validation
→ Parsing

Planned pipeline:

Upload
→ Validation
→ Parsing
→ Chunking
→ Embedding
→ Indexing

## Current Implemented Components

- UploadService
- DocumentIngestionService
- ParserFactory
- BaseParser
- TextParser
- MarkdownParser
- PdfParser
- BasePdfProvider
- PyMuPDFProvider
- StorageService
- Repository Layer
- OperationTracker

## Future Enhancements

- Chunking Engine
- Embedding Framework
- Vector Store Integration
- Background Processing
- Retry Framework
