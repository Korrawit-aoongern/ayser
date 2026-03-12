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
  - Anomaly detection (Isolation Forest)
  - Rule-based fallback
- LLM:
  - Gemini (for health explanation and advisory narrative)

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
 - JWT (Cookie)

## Observability
### Monitoring
- HTTP-based health checks
  - Black-box monitoring (URL-based)
  - Gray-box monitoring (URL + /metrics endpoint)

## Architecture Style
- Modular Monolith
  - Clear separation by domain (Frontend, Backend, ML)
## Repository
 - Gitlab
 - Github
## CI/CD Pipeline
 - Gitlab
## Containerization
- Docker + Compose
## Deployment Target
    Frontend App = Vercel /
    Backend App =   Render.io /
                    AWS Lambda (alternative)
                    Render.io (alternative)
                    Railway (alternative)
    ML Service = Render.io /
    Database = Supabase (managed PostgreSQL) /

## Non-Functional Considerations
- Performance
- Scalability
- Security
- Maintainability

