# Integration Tests

This directory contains development logs and documentation for integration testing.

## Files

- `dev_log.md` - Development log tracking notable findings, issues, and solutions discovered during integration testing

## Usage

The dev log is automatically displayed on the Integration Tests page in the frontend. It can also be accessed via the API endpoint:

```
GET /api/integration-tests/dev-log
```

## Logging Notable Findings

When you discover a notable finding during integration testing:

1. Add an entry to `dev_log.md` following the format in the file
2. Include: Issue, Root Cause, Solution, Files Modified, Status
3. Commit with message: `docs: integration test finding - [brief description]`

See `.cursorrules` for the complete logging rule.
