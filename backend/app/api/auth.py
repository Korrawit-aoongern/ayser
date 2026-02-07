from fastapi import APIRouter, HTTPException, Response
from pydantic import BaseModel, EmailStr
from passlib.context import CryptContext
import jwt
from datetime import datetime, timedelta
import os
import asyncpg
from dotenv import load_dotenv
import hashlib

load_dotenv()
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

# ---- Routes ----
@router.post("/register")
async def register(data: RegisterReq):
    db = await get_db()

    existing = await db.fetchrow(
        "SELECT 1 FROM users WHERE email=$1", data.email
    )
    if existing:
        raise HTTPException(400, "Email already registered")

    user_id = await db.fetchval(
        """
        INSERT INTO users (username, email, password_hash)
        VALUES ($1, $2, $3)
        RETURNING user_id
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
        secure=True,
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
        secure=True,
        samesite="lax"
    )
    return {"message": "Logout successful"}


