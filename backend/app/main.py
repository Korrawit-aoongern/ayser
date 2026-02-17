from fastapi import FastAPI
from .api.routes import router
from dotenv import load_dotenv

load_dotenv()

app = FastAPI(title="Ayser Backend", version="0.1.0")

# Include API routes (all prefixed with /api)
app.include_router(router)

@app.get("/")
def health_check():
    return {"status": "ok", "service": "Ayser Backend"}