## Getting Started

### 1. Traefik - Create Certificates

```bash
mkdir -p certs \
  && openssl req -x509 -nodes -newkey rsa:2048 -keyout certs/local-cert.key -out certs/local-cert.crt -subj "/CN=localhost"
```

These `certs` are volume mapped into traefik, enabling https:
```yaml
volumes:
  - "/var/run/docker.sock:/var/run/docker.sock:ro"
  - "./traefik:/etc/traefik"
  - "./certs:/certs"
```

### 2. Copy .env.example file

```bash
cp .env.example .env
```
Update the environment variables as required

### 3. Build and Run

```bash
docker compose up -d --build
```