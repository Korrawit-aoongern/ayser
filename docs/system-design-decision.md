# System Design Decisions
## `* Subject Can be change`
## Frontend
 - SvelteKit

## Backend
 - FastAPI

## Database
 - Supabase

## ML
- ML Role:
  - Anomaly scoring
  - Health pattern summarization
- LLM:
  - ChatGPT (for health explanation and advisory narrative)

## Security (Static & Pipeline-Level)
 - SonarQube
 - Gitlab-Secret detection

## Testing
### Logic-Level / Unit Testing
 - pytest
### API / Integration Testing
 - OpenAPI (Swagger UI)


# Infra

## Networking
### API & Communication
 - RESTful API
 - JSON over HTTPS
### Authentication & Authorization
 - Supabase Auth (JWT-based)

## Observability
### Monitoring
- HTTP-based health checks
  - Black-box monitoring (URL-based)
  - Gray-box monitoring (URL + /metrics endpoint)

## Architecture Style
- Modular Monolith
  - Clear separation by domain (auth, services, health, metrics)
  - Single deployable backend service
  - Designed to evolve into services if required
## Repository
 - Gitlab
 - Github
## CI/CD Pipeline
 - Gitlab
## Containerization
- Docker + Compose
## Deployment Target
    Frontend App = Vercel (candidate)
    Backend App =   Cloudflare Workers (candidate)
                    AWS Lambda (alternative)
                    Render.io (alternative)
                    Railway (alternative)
    ML Service = Backend-triggered batch or async inference
    Database = Supabase (managed PostgreSQL)

## Non-Functional Considerations
- Performance
- Scalability
- Security
- Maintainability

