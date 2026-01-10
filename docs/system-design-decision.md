# System Design Decisions
## `* Subject Can be change`
## Frontend
 - SvelteKit

## Backend
 - FastAPI

## Database
 - Supabase

## ML
 - ?
 - ML Role: anomaly scoring / pattern summarization

## Security (Static & Pipeline-Level)
 - SonarQube
 - Gitlab-Secret detection

## Testing
### Logic-Level / Unit Testing
 - ? (framework to be selected)
### API / Integration Testing
 - ? (contract & integration focus)


# Infra

## Networking
### API & Communication
 - RESTful API
 - JSON over HTTPS
### Authentication & Authorization
 - Supabase Auth (JWT-based)

## Observability
### Monitoring
 - Prometheus (Local)

## Architecture Style
- ? (leaning towards modular monolith)
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
    ML Service = TBD (batch / async inference)
    Database = Supabase (managed PostgreSQL)

## Non-Functional Considerations
- Performance
- Scalability
- Security
- Maintainability

