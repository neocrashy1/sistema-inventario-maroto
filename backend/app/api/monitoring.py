"""
Monitoring and metrics endpoints
"""

from fastapi import APIRouter, HTTPException, status, Depends, Query
from typing import Optional
import structlog

from app.core.monitoring import (
    metrics_collector, get_metrics_summary, start_monitoring, stop_monitoring
)
from app.core.redis_config import redis_health_check, redis_manager
from app.core.security import get_current_user_from_token

logger = structlog.get_logger()

router = APIRouter(prefix="/monitoring", tags=["Monitoring"])


@router.get("/health")
async def health_check():
    """
    Basic health check endpoint
    """
    try:
        health_status = metrics_collector.get_health_status()
        redis_status = redis_health_check()
        
        overall_status = "healthy"
        if health_status.get("status") != "healthy" or redis_status.get("status") != "healthy":
            overall_status = "degraded"
        
        return {
            "status": overall_status,
            "timestamp": health_status.get("last_check"),
            "services": {
                "application": health_status,
                "redis": redis_status
            }
        }
        
    except Exception as e:
        logger.error(f"Health check error: {e}")
        return {
            "status": "error",
            "message": str(e)
        }


@router.get("/metrics")
async def get_metrics(
    minutes: Optional[int] = Query(60, description="Time window in minutes"),
    current_user: dict = Depends(get_current_user_from_token)
):
    """
    Get comprehensive metrics (requires authentication)
    """
    try:
        # Check if user has monitoring permissions
        user_role = current_user.get("role", "")
        if user_role not in ["admin", "monitor"]:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Monitoring access required"
            )
        
        request_stats = metrics_collector.get_request_stats(minutes)
        system_stats = metrics_collector.get_system_stats()
        endpoint_stats = metrics_collector.get_endpoint_stats()
        error_summary = metrics_collector.get_error_summary()
        health_status = metrics_collector.get_health_status()
        
        return {
            "time_window_minutes": minutes,
            "request_metrics": request_stats,
            "system_metrics": system_stats,
            "endpoint_metrics": endpoint_stats,
            "error_summary": error_summary,
            "health_status": health_status,
            "active_requests": metrics_collector.active_requests,
            "total_requests": metrics_collector.total_requests
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Metrics retrieval error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve metrics"
        )


@router.get("/metrics/requests")
async def get_request_metrics(
    minutes: Optional[int] = Query(60, description="Time window in minutes"),
    current_user: dict = Depends(get_current_user_from_token)
):
    """
    Get request-specific metrics
    """
    try:
        user_role = current_user.get("role", "")
        if user_role not in ["admin", "monitor"]:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Monitoring access required"
            )
        
        return metrics_collector.get_request_stats(minutes)
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Request metrics error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve request metrics"
        )


@router.get("/metrics/system")
async def get_system_metrics(
    current_user: dict = Depends(get_current_user_from_token)
):
    """
    Get system performance metrics
    """
    try:
        user_role = current_user.get("role", "")
        if user_role not in ["admin", "monitor"]:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Monitoring access required"
            )
        
        return metrics_collector.get_system_stats()
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"System metrics error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve system metrics"
        )


@router.get("/metrics/endpoints")
async def get_endpoint_metrics(
    current_user: dict = Depends(get_current_user_from_token)
):
    """
    Get endpoint performance metrics
    """
    try:
        user_role = current_user.get("role", "")
        if user_role not in ["admin", "monitor"]:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Monitoring access required"
            )
        
        endpoint_stats = metrics_collector.get_endpoint_stats()
        
        # Sort by request count
        sorted_endpoints = sorted(
            endpoint_stats.items(),
            key=lambda x: x[1]['count'],
            reverse=True
        )
        
        return {
            "total_endpoints": len(endpoint_stats),
            "endpoints": dict(sorted_endpoints)
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Endpoint metrics error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve endpoint metrics"
        )


@router.get("/metrics/errors")
async def get_error_metrics(
    current_user: dict = Depends(get_current_user_from_token)
):
    """
    Get error metrics and summary
    """
    try:
        user_role = current_user.get("role", "")
        if user_role not in ["admin", "monitor"]:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Monitoring access required"
            )
        
        error_summary = metrics_collector.get_error_summary()
        total_errors = sum(error_summary.values())
        
        return {
            "total_errors": total_errors,
            "error_breakdown": error_summary,
            "error_rate_last_hour": metrics_collector.get_request_stats(60).get("error_rate", 0)
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error metrics error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve error metrics"
        )


@router.get("/status/redis")
async def get_redis_status(
    current_user: dict = Depends(get_current_user_from_token)
):
    """
    Get Redis connection and performance status
    """
    try:
        user_role = current_user.get("role", "")
        if user_role not in ["admin", "monitor"]:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Monitoring access required"
            )
        
        redis_status = redis_health_check()
        
        # Additional Redis info if connected
        additional_info = {}
        if redis_manager.is_connected:
            try:
                info = redis_manager.redis_client.info()
                additional_info = {
                    "connected_clients": info.get("connected_clients", 0),
                    "used_memory_human": info.get("used_memory_human", "N/A"),
                    "keyspace_hits": info.get("keyspace_hits", 0),
                    "keyspace_misses": info.get("keyspace_misses", 0),
                    "total_commands_processed": info.get("total_commands_processed", 0)
                }
                
                # Calculate hit rate
                hits = info.get("keyspace_hits", 0)
                misses = info.get("keyspace_misses", 0)
                if hits + misses > 0:
                    additional_info["hit_rate"] = round((hits / (hits + misses)) * 100, 2)
                
            except Exception as e:
                logger.warning(f"Could not get Redis info: {e}")
        
        return {
            **redis_status,
            "additional_info": additional_info
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Redis status error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve Redis status"
        )


@router.post("/control/start")
async def start_monitoring_endpoint(
    current_user: dict = Depends(get_current_user_from_token)
):
    """
    Start performance monitoring (admin only)
    """
    try:
        if current_user.get("role") != "admin":
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Admin access required"
            )
        
        start_monitoring()
        logger.info(f"Monitoring started by admin user {current_user.get('email')}")
        
        return {"message": "Performance monitoring started"}
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Start monitoring error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to start monitoring"
        )


@router.post("/control/stop")
async def stop_monitoring_endpoint(
    current_user: dict = Depends(get_current_user_from_token)
):
    """
    Stop performance monitoring (admin only)
    """
    try:
        if current_user.get("role") != "admin":
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Admin access required"
            )
        
        stop_monitoring()
        logger.info(f"Monitoring stopped by admin user {current_user.get('email')}")
        
        return {"message": "Performance monitoring stopped"}
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Stop monitoring error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to stop monitoring"
        )


@router.get("/dashboard")
async def get_monitoring_dashboard(
    current_user: dict = Depends(get_current_user_from_token)
):
    """
    Get comprehensive monitoring dashboard data
    """
    try:
        user_role = current_user.get("role", "")
        if user_role not in ["admin", "monitor"]:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Monitoring access required"
            )
        
        # Get all metrics for dashboard
        request_stats_1h = metrics_collector.get_request_stats(60)
        request_stats_24h = metrics_collector.get_request_stats(1440)
        system_stats = metrics_collector.get_system_stats()
        health_status = metrics_collector.get_health_status()
        redis_status = redis_health_check()
        
        # Get top endpoints
        endpoint_stats = metrics_collector.get_endpoint_stats()
        top_endpoints = sorted(
            endpoint_stats.items(),
            key=lambda x: x[1]['count'],
            reverse=True
        )[:10]
        
        # Get slowest endpoints
        slowest_endpoints = sorted(
            endpoint_stats.items(),
            key=lambda x: x[1]['avg_response_time'],
            reverse=True
        )[:5]
        
        return {
            "overview": {
                "health_status": health_status,
                "active_requests": metrics_collector.active_requests,
                "total_requests": metrics_collector.total_requests,
                "uptime_seconds": system_stats.get("uptime_seconds", 0)
            },
            "performance": {
                "last_hour": request_stats_1h,
                "last_24_hours": request_stats_24h,
                "system": system_stats
            },
            "endpoints": {
                "top_by_requests": dict(top_endpoints),
                "slowest": dict(slowest_endpoints)
            },
            "services": {
                "redis": redis_status
            }
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Dashboard data error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve dashboard data"
        )