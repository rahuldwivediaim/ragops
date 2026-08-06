# Error Handling

## Standard Response

```json
{
  "code":"DOCUMENT_NOT_FOUND",
  "message":"Document does not exist",
  "traceId":"..."
}
```

## Error Categories
- Validation
- Business
- Infrastructure
- External Provider
- Authentication
- Authorization

Every request carries a correlation ID.
