from fastapi import APIRouter, HTTPException, Depends
from typing import List

from ..schemas.service import ServiceCreate, ServiceUpdate, ServiceResponse
import asyncpg
import os
from .auth import require_user

router = APIRouter(prefix="/services", tags=["services"])


async def get_db():
    return await asyncpg.connect(os.getenv("DATABASE_URL"), statement_cache_size=0)


@router.get("", response_model=List[ServiceResponse])
async def get_all_services(user_id=Depends(require_user)):
    """Get all services for the current user"""

    db = await get_db()
    try:
        services = await db.fetch(
            """
            SELECT
                s.service_id,
                s.user_id,
                s.service_name,
                s.service_url,
                s.check_type,
                s.created_at,
                h.availability,
                h.checked_at
            FROM services s
            LEFT JOIN LATERAL (
                SELECT availability, checked_at
                FROM service_health
                WHERE service_id = s.service_id
                ORDER BY checked_at DESC
                LIMIT 1
            ) h ON TRUE
            WHERE s.user_id = $1
            ORDER BY s.created_at
            """,
            user_id
        )

        return [dict(service) for service in services]
    finally:
        await db.close()


@router.get("/{service_id}", response_model=ServiceResponse)
async def get_service(service_id: int, user_id=Depends(require_user)):
    """Get specific service by ID"""
    db = await get_db()
    try:
        service = await db.fetchrow(
            "SELECT service_id, user_id, service_name, service_url, check_type, created_at FROM services WHERE service_id=$1 AND user_id=$2",
            service_id, user_id
        )
        
        if not service:
            raise HTTPException(status_code=404, detail="Service not found")
        
        return dict(service)
    finally:
        await db.close()


@router.post("", response_model=ServiceResponse)
async def create_service(service: ServiceCreate, user_id=Depends(require_user)):
    """Create new service"""
    db = await get_db()
    try:
        service_id = await db.fetchval(
            """
            INSERT INTO services (user_id, service_name, service_url, check_type)
            VALUES ($1, $2, $3, $4)
            RETURNING service_id
            """,
            user_id, service.service_name, service.service_url, service.check_type
        )
        
        created = await db.fetchrow(
            "SELECT service_id, user_id, service_name, service_url, check_type, created_at FROM services WHERE service_id=$1",
            service_id
        )
        
        return dict(created)
    finally:
        await db.close()


@router.put("/{service_id}", response_model=ServiceResponse)
async def update_service(service_id: int, service: ServiceUpdate, user_id=Depends(require_user)):
    """Update service"""
    db = await get_db()
    try:
        existing = await db.fetchrow(
            "SELECT service_id FROM services WHERE service_id=$1 AND user_id=$2",
            service_id, user_id
        )
        
        if not existing:
            raise HTTPException(status_code=404, detail="Service not found")
        
        update_data = service.model_dump(exclude_unset=True)
        
        # Build dynamic update query
        set_clauses = []
        params = []
        for i, (key, value) in enumerate(update_data.items(), 1):
            set_clauses.append(f"{key}=${i}")
            params.append(value)
        
        params.append(service_id)
        params.append(user_id)
        
        if set_clauses:
            query = f"""
                UPDATE services 
                SET {', '.join(set_clauses)}
                WHERE service_id=${len(params)-1} AND user_id=${len(params)}
                RETURNING service_id, user_id, service_name, service_url, check_type, created_at
            """
            updated = await db.fetchrow(query, *params)
        else:
            updated = await db.fetchrow(
                "SELECT service_id, user_id, service_name, service_url, check_type, created_at FROM services WHERE service_id=$1",
                service_id
            )
        
        return dict(updated)
    finally:
        await db.close()


@router.delete("/{service_id}")
async def delete_service(service_id: int, user_id=Depends(require_user)):
    """Delete service"""
    db = await get_db()
    try:
        result = await db.execute(
            "DELETE FROM services WHERE service_id=$1 AND user_id=$2",
            service_id, user_id
        )
        
        if result == "DELETE 0":
            raise HTTPException(status_code=404, detail="Service not found")
        
        return {"message": f"Service {service_id} deleted"}
    finally:
        await db.close()


@router.delete("")
async def delete_all_services(user_id=Depends(require_user)):
    """Delete all services for current user"""
    db = await get_db()
    try:
        deleted_count = await db.fetchval(
            "SELECT COUNT(*) FROM services WHERE user_id=$1",
            user_id
        )

        await db.execute(
            "DELETE FROM services WHERE user_id=$1",
            user_id
        )

        return {
            "message": "All services deleted",
            "deleted_count": int(deleted_count or 0)
        }
    finally:
        await db.close()

