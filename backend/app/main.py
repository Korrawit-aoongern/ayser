from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from api.routes import router
import os
from dotenv import load_dotenv

load_dotenv()

app = FastAPI(title="Ayser Backend", version="0.1.0")

# CORS middleware - Allow specific origins for cookie-based authentication
allowed_origins = os.getenv("ALLOWED_ORIGINS", "http://localhost:5173").split(",")

app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include API routes (all prefixed with /api)
app.include_router(router)

@app.get("/health")
def health_check():
    return {"status": "ok", "service": "Ayser Backend"}