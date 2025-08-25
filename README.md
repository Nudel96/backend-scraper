# PAT Backend

Backend service ingesting events and serving bias heatmap scores.

## Running locally

```bash
docker compose -f docker/compose.yml up --build
```

## Sample usage

Post a batch of events:

```bash
curl -X POST http://localhost:8000/ingest/events \
  -H 'Content-Type: application/json' \
  -d '{"events":[{"schema_version":"2025.08.1","source":"test","asset":"XAUUSD","kind":"indicator","ingested_at":"2024-01-01T00:00:00Z","payload":{"key":"macro","value":5},"trace_id":"00000000-0000-0000-0000-000000000001"}]}'
```

Fetch heatmap score:

```bash
curl http://localhost:8000/heatmap?asset=XAUUSD
```
