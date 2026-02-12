from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from .api.routes import router
import os
from dotenv import load_dotenv

load_dotenv()

app = FastAPI(title="Ayser Backend", version="0.1.0")

# CORS middleware - Allow localhost variants for development
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://127.0.0.1:5173",
        "http://localhost:3000",
        "http://127.0.0.1:3000",
    ],
    allow_origin_regex=r"http://localhost.*",
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include API routes (all prefixed with /api)
app.include_router(router)

@app.get("/health")
def health_check():
    return {"status": "ok", "service": "Ayser Backend"}