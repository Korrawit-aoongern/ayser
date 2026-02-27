from fastapi import APIRouter, HTTPException, Depends
from typing import List

from ..schemas.service import ServiceCreate, ServiceUpdate, ServiceResponse
import asyncpg
import os
from .auth import require_user

router = APIRouter(prefix="/services", tags=["services"])


async def get_db():
    return await asyncpg.connect(os.getenv("DATABASE_URL"), statement_cache_size=0)


def _normalize_metrics_endpoint(value):
    cleaned = (value or "").strip()
    return cleaned if cleaned else "/metrics"


def _with_default_metrics_endpoint(row):
    payload = dict(row)
    payload["metrics_endpoint"] = payload.get("metrics_endpoint") or "/metrics"
    return payload


@router.get("", response_model=List[ServiceResponse])
async def get_all_services(user_id=Depends(require_user)):
    """Get all services for the current user"""

    db = await get_db()
    try:
        try:
            services = await db.fetch(
                """
                SELECT
                    s.service_id,
                    s.user_id,
                    s.service_name,
                    s.service_url,
                    s.check_type,
                    s.metrics_endpoint,
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
            return [_with_default_metrics_endpoint(service) for service in services]
        except asyncpg.UndefinedColumnError:
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
            return [_with_default_metrics_endpoint(service) for service in services]
    finally:
        await db.close()


@router.get("/{service_id}", response_model=ServiceResponse)
async def get_service(service_id: int, user_id=Depends(require_user)):
    """Get specific service by ID"""
    db = await get_db()
    try:
        try:
            service = await db.fetchrow(
                "SELECT service_id, user_id, service_name, service_url, check_type, metrics_endpoint, created_at FROM services WHERE service_id=$1 AND user_id=$2",
                service_id, user_id
            )
        except asyncpg.UndefinedColumnError:
            service = await db.fetchrow(
                "SELECT service_id, user_id, service_name, service_url, check_type, created_at FROM services WHERE service_id=$1 AND user_id=$2",
                service_id, user_id
            )
        
        if not service:
            raise HTTPException(status_code=404, detail="Service not found")
        
        return _with_default_metrics_endpoint(service)
    finally:
        await db.close()


@router.post("", response_model=ServiceResponse)
async def create_service(service: ServiceCreate, user_id=Depends(require_user)):
    """Create new service"""
    db = await get_db()
    try:
        metrics_endpoint = _normalize_metrics_endpoint(service.metrics_endpoint)

        try:
            service_id = await db.fetchval(
                """
                INSERT INTO services (user_id, service_name, service_url, check_type, metrics_endpoint)
                VALUES ($1, $2, $3, $4, $5)
                RETURNING service_id
                """,
                user_id, service.service_name, service.service_url, service.check_type, metrics_endpoint
            )
            
            created = await db.fetchrow(
                "SELECT service_id, user_id, service_name, service_url, check_type, metrics_endpoint, created_at FROM services WHERE service_id=$1",
                service_id
            )
        except asyncpg.UndefinedColumnError:
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
        
        return _with_default_metrics_endpoint(created)
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
        if "metrics_endpoint" in update_data:
            update_data["metrics_endpoint"] = _normalize_metrics_endpoint(update_data["metrics_endpoint"])
        
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
                RETURNING service_id, user_id, service_name, service_url, check_type, metrics_endpoint, created_at
            """
            try:
                updated = await db.fetchrow(query, *params)
            except asyncpg.UndefinedColumnError:
                fallback_data = {k: v for k, v in update_data.items() if k != "metrics_endpoint"}
                fallback_set_clauses = []
                fallback_params = []
                for i, (key, value) in enumerate(fallback_data.items(), 1):
                    fallback_set_clauses.append(f"{key}=${i}")
                    fallback_params.append(value)
                fallback_params.append(service_id)
                fallback_params.append(user_id)

                if fallback_set_clauses:
                    fallback_query = f"""
                        UPDATE services
                        SET {', '.join(fallback_set_clauses)}
                        WHERE service_id=${len(fallback_params)-1} AND user_id=${len(fallback_params)}
                        RETURNING service_id, user_id, service_name, service_url, check_type, created_at
                    """
                    updated = await db.fetchrow(fallback_query, *fallback_params)
                else:
                    updated = await db.fetchrow(
                        "SELECT service_id, user_id, service_name, service_url, check_type, created_at FROM services WHERE service_id=$1",
                        service_id
                    )
        else:
            try:
                updated = await db.fetchrow(
                    "SELECT service_id, user_id, service_name, service_url, check_type, metrics_endpoint, created_at FROM services WHERE service_id=$1",
                    service_id
                )
            except asyncpg.UndefinedColumnError:
                updated = await db.fetchrow(
                    "SELECT service_id, user_id, service_name, service_url, check_type, created_at FROM services WHERE service_id=$1",
                    service_id
                )
        
        return _with_default_metrics_endpoint(updated)
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

