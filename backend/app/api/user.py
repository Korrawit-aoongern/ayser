from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, EmailStr
import asyncpg
import os

from .auth import require_user, hash_password, verify_password

router = APIRouter(prefix="/user", tags=["user"])


async def get_db():
    return await asyncpg.connect(os.getenv("DATABASE_URL"), statement_cache_size=0)


class UserUpdateRequest(BaseModel):
    username: str
    email: EmailStr


class PasswordChangeRequest(BaseModel):
    old_password: str
    new_password: str


@router.get("")
async def get_current_user(user_id=Depends(require_user)):
    db = await get_db()
    try:
        user = await db.fetchrow(
            "SELECT user_id, username, email FROM users WHERE user_id=$1",
            user_id
        )
        if not user:
            raise HTTPException(status_code=404, detail="User not found")

        return {
            "user_id": str(user["user_id"]),
            "username": user["username"],
            "email": user["email"]
        }
    finally:
        await db.close()


@router.put("")
async def update_current_user(data: UserUpdateRequest, user_id=Depends(require_user)):
    db = await get_db()
    try:
        existing_email = await db.fetchrow(
            "SELECT user_id FROM users WHERE email=$1 AND user_id != $2",
            data.email,
            user_id
        )
        if existing_email:
            raise HTTPException(status_code=400, detail="Email already registered")

        updated = await db.fetchrow(
            """
            UPDATE users
            SET username=$1, email=$2
            WHERE user_id=$3
            RETURNING user_id, username, email
            """,
            data.username,
            data.email,
            user_id
        )
        if not updated:
            raise HTTPException(status_code=404, detail="User not found")

        return {
            "message": "User updated successfully",
            "user": {
                "user_id": str(updated["user_id"]),
                "username": updated["username"],
                "email": updated["email"]
            }
        }
    finally:
        await db.close()


@router.put("/password")
async def change_password(data: PasswordChangeRequest, user_id=Depends(require_user)):
    db = await get_db()
    try:
        user = await db.fetchrow(
            "SELECT password_hash FROM users WHERE user_id=$1",
            user_id
        )
        if not user:
            raise HTTPException(status_code=404, detail="User not found")

        if not verify_password(data.old_password, user["password_hash"]):
            raise HTTPException(status_code=400, detail="Old password is incorrect")

        if data.old_password == data.new_password:
            raise HTTPException(status_code=400, detail="New password must be different")

        await db.execute(
            "UPDATE users SET password_hash=$1 WHERE user_id=$2",
            hash_password(data.new_password),
            user_id
        )

        return {
            "message": "Password changed successfully",
            "force_logout": True
        }
    finally:
        await db.close()


@router.delete("")
async def delete_current_user(user_id=Depends(require_user)):
    db = await get_db()
    try:
        deleted = await db.fetchval(
            "DELETE FROM users WHERE user_id=$1 RETURNING user_id",
            user_id
        )
        if not deleted:
            raise HTTPException(status_code=404, detail="User not found")

        return {"message": "User deleted successfully"}
    finally:
        await db.close()
