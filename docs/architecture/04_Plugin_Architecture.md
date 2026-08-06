# Plugin Architecture

## Goals
- Hot-pluggable providers
- Stable interfaces
- Versioned manifests

## Plugin Layout
```
plugin/
 manifest.yaml
 adapter.py
 config.py
 tests/
```

## Lifecycle
Load -> Validate -> Register -> Health Check -> Serve -> Unload
