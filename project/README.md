# The Filter Factory

A containerized REST API for managing malicious URLs via a denylist/allowlist, designed for easy deployment with Docker Compose and secured behind Nginx with HTTPS.
Tasks and requirements can be found [here](docs/projectRequirements.md)

---

## Table of Contents

- [The Filter Factory](#the-filter-factory)
  - [Table of Contents](#table-of-contents)
  - [Overview](#overview)
  - [Architecture, Design \& Components](#architecture-design--components)
  - [File Structure](#file-structure)
  - [Configuration \& Environment](#configuration--environment)
  - [Database Initialization](#database-initialization)
  - [Docker Compose Services](#docker-compose-services)
  - [Api Reference](#api-reference)
  - [Logging](#logging)
  - [Scalability \& High Availability](#scalability--high-availability)

---

## Overview

**The Filter Factory** is a Python 3.11 Flask application that:

- **Fetches** a live list of malicious URLs from [urlhaus.abuse.ch](https://urlhaus.abuse.ch/downloads/text/).
- **Persists** them in PostgreSQL to avoid hammering the upstream service.
- **Exposes** a programmatic API to view the denylist and manage an allowlist.
- **Runs** behind Nginx with TLS termination.
- **Packages** everything in Docker containers, orchestrated by Docker Compose.

---

## Architecture, Design & Components

- **API Service** (`the-filter-factory`):
  - **Flask** web framework
  - **SQLAlchemy** ORM with PostgreSQL backend
  - **Requests + Retry** for robust upstream fetch
  - **Gunicorn** WSGI server (production)
- **Database**: PostgreSQL, initialized via SQL scripts.
- **Reverse Proxy**: Nginx (listening on 80/443, TLS certs in `config/certs`).
- **Orchestration**: Docker Compose networking, healthchecks, and volume mounts.
- **Docker** + **Docker Compose** for containerization

---

## File Structure

```txt
the-filter-factory/
├── Dockerfile
├── config
│   ├── certs
│   │   ├── tls.crt
│   │   └── tls.key
│   ├── nginx
│   │   ├── conf.d
│   │   │   └── api.conf
│   │   └── nginx.conf
│   └── scripts
│       └── 00_init_db.sql
├── docker-compose.yaml
├── docs
│   ├── README.md
│   ├── api.md
│   └── docker.md
├── docs.md
└── the-filter-factory
    ├── Dockerfile
    ├── README.md
    ├── main.py
    ├── modules
    │   ├── db.py
    │   └── functions.py
    └── requirements.txt
```

---

## Configuration & Environment

1. Copy `the-filter-factory/.env.sample` → `the-filter-factory/.env`
2. Edit as needed:

| Variable       | Description                          | Example                                                  |
|----------------|--------------------------------------|----------------------------------------------------------|
| `DATABASE_URI` | PostgreSQL connection URI            | `postgresql://postgres:admin@db:5432/the_filter_factory` |
| `HOST`         | Flask listen host (for developement) | `0.0.0.0`                                                |
| `PORT`         | Flask listen port (for developement) | `8000`                                                   |

3. Place TLS cert & key in `config/certs/tls.crt` + `tls.key`.
4. Customize Nginx if needed in `config/nginx/nginx.conf` and `conf.d/api.conf`.

---

## Database Initialization

On first run, the Postgres container executes any `.sql` files under `/docker-entrypoint-initdb.d`. We include:

- `00_init_db.sql`:
```sql
CREATE DATABASE the_filter_factory;
-- You can add schema migrations here if needed
```

---

## Docker Compose Services

Read more about Docker Compose services [here](docs/dockercompose.md)

---

## Api Reference

For more information on app API look [here](docs/api.md)

---

## Logging

- Log statements via Loguru (configured in main.py).
- Captures request errors, DB errors, and unhandled exceptions.

---

## Scalability & High Availability

- Stateless Flask app behind Gunicorn allows horizontal scaling.

```bash
docker-compose up -d --scale api=3
```

- Add a load balancer (e.g., Traefik, Nginx, ELB) to distribute traffic across instances.
- Ensure all instances share the same PostgreSQL database (or use a managed cluster).
