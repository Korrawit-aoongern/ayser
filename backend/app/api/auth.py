from fastapi import APIRouter, HTTPException
from schemas.auth import LoginRequest, LoginResponse

router = APIRouter(prefix="/auth", tags=["auth"])

# Mock users - replace with database later
USERS = {
    "test@example.com": "password"
}

@router.post("/login", response_model=LoginResponse)
def login(request: LoginRequest):
    """Login endpoint - returns JWT token"""
    if request.email not in USERS or USERS[request.email] != request.password:
        raise HTTPException(status_code=401, detail="Invalid credentials")
    
    # TODO: Generate JWT token
    return {
        "access_token": "mock-jwt-token-12345",
        "token_type": "bearer"
    }

@router.post("/logout")
def logout():
    """Logout endpoint"""
    return {"message": "Logged out successfully"}
