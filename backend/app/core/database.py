"""
Database configuration and session management
"""

from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker
from sqlalchemy.orm import declarative_base, sessionmaker
from sqlalchemy import create_engine
from sqlalchemy.pool import NullPool
import structlog

from app.core.config import settings

logger = structlog.get_logger()

# Create async engine with optimized settings
# Adjust pooling options based on the database driver (SQLite doesn't support pool_size/max_overflow)
_async_url = settings.ASYNC_DATABASE_URL or settings.DATABASE_URL
if _async_url and "sqlite" in _async_url:
    async_engine = create_async_engine(
        _async_url,
        echo=settings.DEBUG,
        poolclass=NullPool,
    )
else:
    async_engine = create_async_engine(
        _async_url,
        echo=settings.DEBUG,
        pool_pre_ping=True,
        pool_recycle=3600,      # Recycle connections every hour
        pool_size=10,           # Base pool size
        max_overflow=20,        # Additional connections when needed
        pool_timeout=30,        # Timeout to get connection
    )

# Create sync engine for migrations and optimizations
_sync_url = settings.DATABASE_URL_SYNC
if _sync_url and "sqlite" in _sync_url:
    sync_engine = create_engine(
        _sync_url,
        echo=settings.DEBUG,
        poolclass=NullPool,
    )
else:
    sync_engine = create_engine(
        _sync_url,
        echo=settings.DEBUG,
        pool_pre_ping=True,
        pool_recycle=3600,      # Recycle connections every hour
        pool_size=10,           # Base pool size
        max_overflow=20,        # Additional connections when needed
        pool_timeout=30,        # Timeout to get connection
    )

# Export sync engine for optimizations
engine = sync_engine

# Create async session factory
AsyncSessionLocal = async_sessionmaker(
    async_engine,
    class_=AsyncSession,
    expire_on_commit=False
)

# Create sync session factory
SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=sync_engine
)

# Create declarative base
Base = declarative_base()


async def get_async_session() -> AsyncSession:
    """Get async database session"""
    async with AsyncSessionLocal() as session:
        try:
            yield session
        except Exception as e:
            await session.rollback()
            logger.error("Database session error", error=str(e))
            raise
        finally:
            await session.close()


def get_sync_session():
    """Get sync database session"""
    session = SessionLocal()
    try:
        yield session
    except Exception as e:
        session.rollback()
        logger.error("Database session error", error=str(e))
        raise
    finally:
        session.close()


# Alias for compatibility
get_db = get_sync_session


async def init_db():
    """Initialize database with optimizations"""
    try:
        # Import all models to ensure they are registered
        from app.models import user, asset, location, alert, ticket, movement, machine
        
        # Create tables
        async with async_engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)
            
        logger.info("Database tables created successfully")
        
        # Apply performance optimizations
        try:
            from app.core.database_optimizations import run_all_optimizations
            run_all_optimizations()
            logger.info("Database optimizations applied successfully")
        except Exception as e:
            logger.warning(f"Could not apply database optimizations: {e}")
            
    except Exception as e:
        logger.error(f"Failed to initialize database: {e}")
        raise


async def close_db():
    """Close database connections"""
    await async_engine.dispose()
    sync_engine.dispose()
    logger.info("Database connections closed")