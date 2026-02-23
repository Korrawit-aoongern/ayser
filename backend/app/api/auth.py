from fastapi import APIRouter, HTTPException, Response, Depends, Request
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials

from pydantic import BaseModel, EmailStr
from passlib.context import CryptContext
import jwt
from datetime import datetime, timedelta
import os
import asyncpg
from dotenv import load_dotenv
import hashlib

load_dotenv()
security = HTTPBearer(auto_error=False)
router = APIRouter(prefix="/auth", tags=["auth"])

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

JWT_SECRET = os.getenv("JWT_SECRET", "dev-secret")
JWT_ALGO = "HS256"
JWT_EXPIRE_MIN = 60 * 24 * 7  # 7 days

# ---- DB ----
async def get_db():
    return await asyncpg.connect(os.getenv("DATABASE_URL"))

# ---- Models ----
class RegisterReq(BaseModel):
    username: str
    email: EmailStr
    password: str

class LoginReq(BaseModel):
    email: EmailStr
    password: str

# ---- Helpers ----
def hash_password(pw: str) -> str:
    pw = hashlib.sha256(pw.encode()).hexdigest()
    return pwd_context.hash(pw)

def verify_password(pw: str, hashed: str) -> bool:
    pw = hashlib.sha256(pw.encode()).hexdigest()
    return pwd_context.verify(pw, hashed)

def create_jwt(user_id: str):
    payload = {
        "sub": user_id,
        "exp": datetime.utcnow() + timedelta(minutes=JWT_EXPIRE_MIN)
    }
    return jwt.encode(payload, JWT_SECRET, algorithm=JWT_ALGO)
def require_user(
    request: Request,
    credentials: HTTPAuthorizationCredentials | None = Depends(security)
):
    token = credentials.credentials if credentials else request.cookies.get("access_token")
    if not token:
        raise HTTPException(status_code=401, detail="Not authenticated")

    try:
        payload = jwt.decode(
            token,
            JWT_SECRET,
            algorithms=[JWT_ALGO]
        )
        return payload["sub"]  # this is user_id
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Token expired")
    except Exception:
        raise HTTPException(status_code=401, detail="Invalid token")

# ---- Routes ----
@router.post("/register")
async def register(data: RegisterReq):
    db = await get_db()

    existing = await db.fetchrow(
        "SELECT 1 FROM users WHERE email=$1", data.email
    )
    if existing:
        raise HTTPException(400, "Email already registered")

    await db.execute(
        """
        INSERT INTO users (username, email, password_hash)
        VALUES ($1, $2, $3)
        """,
        data.username,
        data.email,
        hash_password(data.password)
    )


    await db.close()
    return {"message": "User registered successfully"}

@router.post("/login")
async def login(data: LoginReq, response: Response):
    db = await get_db()

    user = await db.fetchrow(
        "SELECT user_id, password_hash FROM users WHERE email=$1",
        data.email
    )
    if not user or not verify_password(data.password, user["password_hash"]):
        raise HTTPException(401, "Invalid credentials")

    token = create_jwt(str(user["user_id"]))
    
    # Set secure HTTP-only cookie
    response.set_cookie(
        key="access_token",
        value=token,
        httponly=True,
        secure=False,  # Set to True in production with HTTPS
        samesite="lax",
        max_age=7*24*60*60  # 7 days
    )
    
    await db.close()
    return {"message": "Login successful"}

@router.post("/logout")
async def logout(response: Response):
    # Clear the access token cookie
    response.delete_cookie(
        key="access_token",
        httponly=True,
        secure=False,
        samesite="lax"
    )
    return {"message": "Logout successful"}


