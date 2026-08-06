# Low Level Design (Expanded)

## Dependency Rules
- `common` may be imported by all modules.
- Feature modules communicate through public service interfaces.
- No circular dependencies.

## Request Lifecycle
1. HTTP Request
2. Router
3. Validation
4. Service
5. Repository
6. Provider Adapter (if required)
7. Response Mapping
8. Audit & Metrics

## Transaction Boundaries
Transactions are owned by the service layer. Repository methods must not begin or commit transactions.

## Testing Strategy
- Unit tests for services
- Repository integration tests
- API contract tests
- End-to-end workflows
