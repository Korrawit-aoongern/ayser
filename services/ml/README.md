# Ayser ML Service

Isolation Forest microservice for per-service anomaly evaluation.

## Run locally

```bash
cd services/ml
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
uvicorn app.main:app --host 0.0.0.0 --port 8010 --reload
```

Optional env for testing:

```bash
set ML_MIN_SAMPLES=5
```

Default is `50`.

## API

- `GET /` health check
- `POST /evaluate` evaluate anomaly on numeric samples
- `GET /metrics` dev Prometheus-style metrics endpoint for testing Ayser scraping

## Dev Metrics Profiles

The `/metrics` endpoint can output unhealthy or normal metrics:

```bash
set DEMO_METRICS_PROFILE=bad
# or
set DEMO_METRICS_PROFILE=normal
```

Default is `bad`.
