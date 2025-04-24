# API Endpoints

1. Health Check

```http
GET /health
```

Response:

- 200 OK

```json
{ "status": "UP" }
```

- 500 Internal Server Error

```json
{ "status": "DOWN" }
```

2. Get Denylist

```http
GET /denylist
```

Fetches fresh data, syncs local DB, prunes stale entries, and returns the denylist minus any allowlisted URLs.

Response:

- 200 OK

```json
[
  "http://malicious.example/1",
  "http://bad.example/path",
  …
]
```

3. Get Allowlist

```json
GET /allowlist
```

Returns all URLs you’ve posted to the allowlist.

Response:

- 200 OK

```json
[
  "http://falsepositive.example",
  …
]
```

4. Add to Allowlist

```http
POST /allowlist
Content-Type: application/json

[
  "http://falsepositive.example",
  "http://another.safe/"
]
```

Responses:

- 201 Created

```json
{
  "urls_added": [
    "http://falsepositive.example",
    "http://another.safe/"
  ],
  "message": "URLs added to the allowlist"
}
```

- 400 Bad Request

```json
{ "message": "Data sent must be string array" }
```

- 500 Internal Server Error

```json
{ "error": "Database error" }
```

---

## Health Checks & Monitoring

- The /health endpoint runs a simple SELECT 1 against the DB.
