"""
Machine Monitoring API endpoints for Windows machines
Provides real-time monitoring data collection and retrieval
"""

from fastapi import APIRouter, HTTPException, status, Depends, Query, BackgroundTasks
from typing import Optional, List, Dict, Any
from datetime import datetime, timedelta
import structlog
import psutil
import platform
import socket
import uuid
import json
from sqlalchemy.orm import Session

from app.core.database import get_sync_session
from app.core.security import get_current_user_from_token
from app.models.machine import Machine, MachineStatus, MachineType, OperatingSystem
from app.core.redis_config import redis_manager

logger = structlog.get_logger()

router = APIRouter(prefix="/machines", tags=["Machine Monitoring"])


class WindowsSystemCollector:
    """Collector for Windows system metrics"""
    
    @staticmethod
    def get_cpu_metrics() -> Dict[str, Any]:
        """Collect CPU metrics"""
        try:
            cpu_percent = psutil.cpu_percent(interval=1)
            cpu_count = psutil.cpu_count()
            cpu_count_logical = psutil.cpu_count(logical=True)
            cpu_freq = psutil.cpu_freq()
            
            return {
                "usage_percent": round(cpu_percent, 2),
                "cores_physical": cpu_count,
                "cores_logical": cpu_count_logical,
                "frequency_mhz": round(cpu_freq.current, 2) if cpu_freq else None,
                "frequency_max_mhz": round(cpu_freq.max, 2) if cpu_freq else None,
                "timestamp": datetime.utcnow().isoformat()
            }
        except Exception as e:
            logger.error(f"Error collecting CPU metrics: {e}")
            return {"error": str(e)}
    
    @staticmethod
    def get_memory_metrics() -> Dict[str, Any]:
        """Collect memory metrics"""
        try:
            memory = psutil.virtual_memory()
            swap = psutil.swap_memory()
            
            return {
                "total_gb": round(memory.total / (1024**3), 2),
                "available_gb": round(memory.available / (1024**3), 2),
                "used_gb": round(memory.used / (1024**3), 2),
                "usage_percent": round(memory.percent, 2),
                "swap_total_gb": round(swap.total / (1024**3), 2),
                "swap_used_gb": round(swap.used / (1024**3), 2),
                "swap_usage_percent": round(swap.percent, 2),
                "timestamp": datetime.utcnow().isoformat()
            }
        except Exception as e:
            logger.error(f"Error collecting memory metrics: {e}")
            return {"error": str(e)}
    
    @staticmethod
    def get_disk_metrics() -> Dict[str, Any]:
        """Collect disk metrics"""
        try:
            disk_usage = psutil.disk_usage('/')
            disk_io = psutil.disk_io_counters()
            
            # Get all disk partitions
            partitions = []
            for partition in psutil.disk_partitions():
                try:
                    partition_usage = psutil.disk_usage(partition.mountpoint)
                    partitions.append({
                        "device": partition.device,
                        "mountpoint": partition.mountpoint,
                        "fstype": partition.fstype,
                        "total_gb": round(partition_usage.total / (1024**3), 2),
                        "used_gb": round(partition_usage.used / (1024**3), 2),
                        "free_gb": round(partition_usage.free / (1024**3), 2),
                        "usage_percent": round((partition_usage.used / partition_usage.total) * 100, 2)
                    })
                except PermissionError:
                    continue
            
            return {
                "total_gb": round(disk_usage.total / (1024**3), 2),
                "used_gb": round(disk_usage.used / (1024**3), 2),
                "free_gb": round(disk_usage.free / (1024**3), 2),
                "usage_percent": round((disk_usage.used / disk_usage.total) * 100, 2),
                "read_bytes": disk_io.read_bytes if disk_io else 0,
                "write_bytes": disk_io.write_bytes if disk_io else 0,
                "partitions": partitions,
                "timestamp": datetime.utcnow().isoformat()
            }
        except Exception as e:
            logger.error(f"Error collecting disk metrics: {e}")
            return {"error": str(e)}
    
    @staticmethod
    def get_network_metrics() -> Dict[str, Any]:
        """Collect network metrics"""
        try:
            net_io = psutil.net_io_counters()
            net_connections = len(psutil.net_connections())
            
            # Get network interfaces
            interfaces = []
            for interface, addrs in psutil.net_if_addrs().items():
                interface_stats = psutil.net_if_stats().get(interface)
                interface_info = {
                    "name": interface,
                    "is_up": interface_stats.isup if interface_stats else False,
                    "speed_mbps": interface_stats.speed if interface_stats else 0,
                    "addresses": []
                }
                
                for addr in addrs:
                    interface_info["addresses"].append({
                        "family": str(addr.family),
                        "address": addr.address,
                        "netmask": addr.netmask,
                        "broadcast": addr.broadcast
                    })
                
                interfaces.append(interface_info)
            
            return {
                "bytes_sent": net_io.bytes_sent,
                "bytes_recv": net_io.bytes_recv,
                "packets_sent": net_io.packets_sent,
                "packets_recv": net_io.packets_recv,
                "errors_in": net_io.errin,
                "errors_out": net_io.errout,
                "drops_in": net_io.dropin,
                "drops_out": net_io.dropout,
                "connections_count": net_connections,
                "interfaces": interfaces,
                "timestamp": datetime.utcnow().isoformat()
            }
        except Exception as e:
            logger.error(f"Error collecting network metrics: {e}")
            return {"error": str(e)}
    
    @staticmethod
    def get_system_info() -> Dict[str, Any]:
        """Collect system information"""
        try:
            boot_time = datetime.fromtimestamp(psutil.boot_time())
            uptime = datetime.now() - boot_time
            
            return {
                "hostname": socket.gethostname(),
                "platform": platform.platform(),
                "system": platform.system(),
                "release": platform.release(),
                "version": platform.version(),
                "machine": platform.machine(),
                "processor": platform.processor(),
                "boot_time": boot_time.isoformat(),
                "uptime_seconds": int(uptime.total_seconds()),
                "timestamp": datetime.utcnow().isoformat()
            }
        except Exception as e:
            logger.error(f"Error collecting system info: {e}")
            return {"error": str(e)}


@router.get("/metrics/current")
async def get_current_machine_metrics(
    current_user: dict = Depends(get_current_user_from_token)
):
    """
    Get current machine metrics (CPU, RAM, Disk, Network)
    """
    try:
        collector = WindowsSystemCollector()
        
        metrics = {
            "machine_id": str(uuid.uuid4()),  # In production, this should be persistent
            "cpu": collector.get_cpu_metrics(),
            "memory": collector.get_memory_metrics(),
            "disk": collector.get_disk_metrics(),
            "network": collector.get_network_metrics(),
            "system": collector.get_system_info(),
            "collected_at": datetime.utcnow().isoformat()
        }
        
        # Store metrics in Redis for real-time access
        await redis_manager.set(
            f"machine_metrics:current",
            json.dumps(metrics),
            expire=300  # 5 minutes
        )
        
        return metrics
        
    except Exception as e:
        logger.error(f"Error getting current metrics: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to collect metrics: {str(e)}"
        )


@router.get("/metrics/history")
async def get_machine_metrics_history(
    machine_id: Optional[str] = Query(None, description="Machine ID"),
    hours: int = Query(24, description="Hours of history to retrieve"),
    current_user: dict = Depends(get_current_user_from_token)
):
    """
    Get historical machine metrics
    """
    try:
        # In a real implementation, this would query a time-series database
        # For now, we'll return sample data structure
        
        end_time = datetime.utcnow()
        start_time = end_time - timedelta(hours=hours)
        
        # Sample historical data structure
        history = {
            "machine_id": machine_id or "current",
            "time_range": {
                "start": start_time.isoformat(),
                "end": end_time.isoformat(),
                "hours": hours
            },
            "metrics": {
                "cpu_usage": [],
                "memory_usage": [],
                "disk_usage": [],
                "network_io": []
            },
            "summary": {
                "avg_cpu_usage": 0,
                "avg_memory_usage": 0,
                "avg_disk_usage": 0,
                "total_network_bytes": 0
            }
        }
        
        return history
        
    except Exception as e:
        logger.error(f"Error getting metrics history: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to retrieve metrics history: {str(e)}"
        )


@router.post("/register")
async def register_machine(
    db: Session = Depends(get_sync_session),
    current_user: dict = Depends(get_current_user_from_token)
):
    """
    Register current machine in the system
    """
    try:
        collector = WindowsSystemCollector()
        system_info = collector.get_system_info()
        cpu_info = collector.get_cpu_metrics()
        memory_info = collector.get_memory_metrics()
        disk_info = collector.get_disk_metrics()
        
        # Check if machine already exists
        hostname = system_info.get("hostname")
        existing_machine = db.query(Machine).filter(Machine.hostname == hostname).first()
        
        if existing_machine:
            # Update existing machine
            existing_machine.status = MachineStatus.ONLINE
            existing_machine.agent_last_seen = datetime.utcnow()
            existing_machine.cpu_usage_percent = cpu_info.get("usage_percent")
            existing_machine.ram_usage_percent = memory_info.get("usage_percent")
            existing_machine.disk_usage_percent = disk_info.get("usage_percent")
            existing_machine.uptime_seconds = system_info.get("uptime_seconds")
            
            db.commit()
            db.refresh(existing_machine)
            
            return {
                "message": "Machine updated successfully",
                "machine_id": existing_machine.id,
                "status": "updated"
            }
        else:
            # Create new machine
            new_machine = Machine(
                hostname=hostname,
                machine_id=str(uuid.uuid4()),
                name=hostname,
                machine_type=MachineType.WORKSTATION,
                status=MachineStatus.ONLINE,
                operating_system=OperatingSystem.WINDOWS if "Windows" in system_info.get("system", "") else OperatingSystem.OTHER,
                os_version=system_info.get("version"),
                architecture=system_info.get("machine"),
                cpu_model=system_info.get("processor"),
                cpu_cores=cpu_info.get("cores_physical"),
                ram_total_gb=memory_info.get("total_gb"),
                disk_total_gb=disk_info.get("total_gb"),
                ip_address=socket.gethostbyname(hostname),
                agent_last_seen=datetime.utcnow(),
                last_boot_time=datetime.fromisoformat(system_info.get("boot_time").replace("Z", "+00:00")) if system_info.get("boot_time") else None,
                uptime_seconds=system_info.get("uptime_seconds"),
                cpu_usage_percent=cpu_info.get("usage_percent"),
                ram_usage_percent=memory_info.get("usage_percent"),
                disk_usage_percent=disk_info.get("usage_percent")
            )
            
            db.add(new_machine)
            db.commit()
            db.refresh(new_machine)
            
            return {
                "message": "Machine registered successfully",
                "machine_id": new_machine.id,
                "status": "created"
            }
            
    except Exception as e:
        logger.error(f"Error registering machine: {e}")
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to register machine: {str(e)}"
        )


@router.get("/list")
async def list_machines(
    status: Optional[MachineStatus] = Query(None, description="Filter by status"),
    machine_type: Optional[MachineType] = Query(None, description="Filter by type"),
    limit: int = Query(50, description="Maximum number of machines to return"),
    offset: int = Query(0, description="Number of machines to skip"),
    db: Session = Depends(get_sync_session),
    current_user: dict = Depends(get_current_user_from_token)
):
    """
    List all registered machines with optional filtering
    """
    try:
        query = db.query(Machine)
        
        if status:
            query = query.filter(Machine.status == status)
        
        if machine_type:
            query = query.filter(Machine.machine_type == machine_type)
        
        machines = query.offset(offset).limit(limit).all()
        total_count = query.count()
        
        return {
            "machines": [
                {
                    "id": machine.id,
                    "hostname": machine.hostname,
                    "name": machine.name,
                    "status": machine.status,
                    "machine_type": machine.machine_type,
                    "operating_system": machine.operating_system,
                    "ip_address": machine.ip_address,
                    "cpu_usage_percent": machine.cpu_usage_percent,
                    "ram_usage_percent": machine.ram_usage_percent,
                    "disk_usage_percent": machine.disk_usage_percent,
                    "uptime_seconds": machine.uptime_seconds,
                    "agent_last_seen": machine.agent_last_seen.isoformat() if machine.agent_last_seen else None,
                    "last_boot_time": machine.last_boot_time.isoformat() if machine.last_boot_time else None
                }
                for machine in machines
            ],
            "total_count": total_count,
            "limit": limit,
            "offset": offset
        }
        
    except Exception as e:
        logger.error(f"Error listing machines: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to list machines: {str(e)}"
        )


@router.get("/{machine_id}/metrics")
async def get_machine_metrics(
    machine_id: int,
    db: Session = Depends(get_sync_session),
    current_user: dict = Depends(get_current_user_from_token)
):
    """
    Get current metrics for a specific machine
    """
    try:
        machine = db.query(Machine).filter(Machine.id == machine_id).first()
        
        if not machine:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Machine not found"
            )
        
        # Try to get real-time metrics from Redis
        cached_metrics = await redis_manager.get(f"machine_metrics:{machine_id}")
        
        if cached_metrics:
            return json.loads(cached_metrics)
        else:
            # Return last known metrics from database
            return {
                "machine_id": machine.id,
                "hostname": machine.hostname,
                "status": machine.status,
                "cpu_usage_percent": machine.cpu_usage_percent,
                "ram_usage_percent": machine.ram_usage_percent,
                "disk_usage_percent": machine.disk_usage_percent,
                "uptime_seconds": machine.uptime_seconds,
                "last_updated": machine.agent_last_seen.isoformat() if machine.agent_last_seen else None,
                "source": "database"
            }
            
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting machine metrics: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get machine metrics: {str(e)}"
        )


@router.post("/{machine_id}/metrics")
async def update_machine_metrics(
    machine_id: int,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_sync_session),
    current_user: dict = Depends(get_current_user_from_token)
):
    """
    Update metrics for a specific machine (typically called by agent)
    """
    try:
        machine = db.query(Machine).filter(Machine.id == machine_id).first()
        
        if not machine:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Machine not found"
            )
        
        # Collect current metrics
        collector = WindowsSystemCollector()
        cpu_metrics = collector.get_cpu_metrics()
        memory_metrics = collector.get_memory_metrics()
        disk_metrics = collector.get_disk_metrics()
        system_info = collector.get_system_info()
        
        # Update machine in database
        machine.status = MachineStatus.ONLINE
        machine.agent_last_seen = datetime.utcnow()
        machine.cpu_usage_percent = cpu_metrics.get("usage_percent")
        machine.ram_usage_percent = memory_metrics.get("usage_percent")
        machine.disk_usage_percent = disk_metrics.get("usage_percent")
        machine.uptime_seconds = system_info.get("uptime_seconds")
        
        db.commit()
        
        # Store in Redis for real-time access
        metrics_data = {
            "machine_id": machine_id,
            "cpu": cpu_metrics,
            "memory": memory_metrics,
            "disk": disk_metrics,
            "system": system_info,
            "updated_at": datetime.utcnow().isoformat()
        }
        
        await redis_manager.set(
            f"machine_metrics:{machine_id}",
            json.dumps(metrics_data),
            expire=300  # 5 minutes
        )
        
        return {
            "message": "Metrics updated successfully",
            "machine_id": machine_id,
            "timestamp": datetime.utcnow().isoformat()
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error updating machine metrics: {e}")
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to update machine metrics: {str(e)}"
        )