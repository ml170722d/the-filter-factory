### api

- Build context: ./the-filter-factory
- Image: built locally
- Entrypoint: gunicorn -b 0.0.0.0:8000 main:app
- Env: DATABASE_URI
- Healthcheck:

```yaml
test: ["CMD-SHELL", "curl -f http://localhost:8000/health || exit 1"]
interval: 10s
timeout: 5s
retries: 3
start_period: 5s
```

### db

- Image: `postgres:16`
- Environment:

```yaml
POSTGRES_USER: postgres
POSTGRES_PASSWORD: admin
POSTGRES_DB: the_filter_factory
```

- Volumes:

```yaml
- ./config/scripts:/docker-entrypoint-initdb.d
- pgdata:/var/lib/postgresql/data
```

- Healthcheck:

```yaml
test: ["CMD-SHELL", "pg_isready -U postgres -d postgres"]
interval: 10s
timeout: 5s
retries: 3
start_period: 5s
```

### lb

- Image: `nginx:1.27.5-alpine`
- Ports:

```yaml
- "80:80"
- "443:443"
```

- Volumes:

```yaml
- ./config/nginx/nginx.conf:/etc/nginx/nginx.conf:ro
- ./config/nginx/conf.d/api.conf:/etc/nginx/conf.d/api.conf:ro
- ./config/certs:/etc/nginx/certs:ro
```

- Networks:

```yaml
networks:
  api-net:
    driver: bridge
```
