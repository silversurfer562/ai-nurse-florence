"""
Session Cleanup Service - AI Nurse Florence
Phase 3.4.4: Session Cleanup

Automatic cleanup of expired sessions and session monitoring.
Following Service Layer Architecture and Background Tasks patterns from coding instructions.
"""

import asyncio
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
from dataclasses import dataclass

# Configure logging
logger = logging.getLogger(__name__)

# Import utilities following conditional imports pattern
try:
    from src.models.database import UserDatabase, get_db_session
    from src.utils.config import get_settings
    _has_database = True
except ImportError:
    _has_database = False
    
    # Mock for testing
    class MockUserDatabase:
        @staticmethod
        async def cleanup_expired_sessions(cutoff_time: datetime) -> int:
            return 0
        
        @staticmethod
        async def get_session_stats() -> Dict[str, Any]:
            return {"total_sessions": 0, "active_sessions": 0}
    
    UserDatabase = MockUserDatabase

try:
    from src.utils.redis_cache import get_redis_client
    _has_redis = True
except ImportError:
    _has_redis = False
    
    def get_redis_client():
        return None

@dataclass
class SessionCleanupStats:
    """Statistics from session cleanup operations."""
    cleanup_time: datetime
    expired_sessions_removed: int
    total_sessions_before: int
    total_sessions_after: int
    cleanup_duration_seconds: float
    errors: List[str]

class SessionCleanupService:
    """
    Service for automatic session cleanup and monitoring.
    
    Features:
    - Automatic cleanup of expired sessions
    - Session statistics and monitoring
    - Background task scheduling
    - Performance optimization
    """
    
    def __init__(self):
        self.settings = None
        try:
            self.settings = get_settings()
        except:
            # Fallback settings
            class FallbackSettings:
                SESSION_CLEANUP_INTERVAL_HOURS = 1
                SESSION_EXPIRY_HOURS = 24
                MAX_SESSIONS_PER_USER = 5
            
            self.settings = FallbackSettings()
        
        self.is_running = False
        self.cleanup_task = None
        self.stats_history: List[SessionCleanupStats] = []
        
        logger.info("Session cleanup service initialized")
    
    async def cleanup_expired_sessions(self) -> SessionCleanupStats:
        """
        Clean up expired sessions from the database.
        
        Returns:
            SessionCleanupStats: Statistics from the cleanup operation
        """
        start_time = datetime.utcnow()
        errors = []
        expired_count = 0
        total_before = 0
        total_after = 0
        
        try:
            logger.info("Starting session cleanup...")
            
            # Get current session stats
            try:
                stats_before = await UserDatabase.get_session_stats()
                total_before = stats_before.get("total_sessions", 0)
                logger.info(f"Sessions before cleanup: {total_before}")
            except Exception as e:
                errors.append(f"Failed to get pre-cleanup stats: {str(e)}")
                logger.warning(f"Could not get session stats before cleanup: {e}")
            
            # Calculate cutoff time for expired sessions
            expiry_hours = getattr(self.settings, 'SESSION_EXPIRY_HOURS', 24)
            cutoff_time = datetime.utcnow() - timedelta(hours=expiry_hours)
            
            # Clean up expired sessions
            try:
                expired_count = await UserDatabase.cleanup_expired_sessions(cutoff_time)
                logger.info(f"Removed {expired_count} expired sessions")
            except Exception as e:
                errors.append(f"Failed to cleanup sessions: {str(e)}")
                logger.error(f"Session cleanup failed: {e}")
            
            # Get updated session stats
            try:
                stats_after = await UserDatabase.get_session_stats()
                total_after = stats_after.get("total_sessions", 0)
                logger.info(f"Sessions after cleanup: {total_after}")
            except Exception as e:
                errors.append(f"Failed to get post-cleanup stats: {str(e)}")
                logger.warning(f"Could not get session stats after cleanup: {e}")
            
            # Clean up Redis cache if available
            if _has_redis:
                try:
                    await self._cleanup_redis_sessions(cutoff_time)
                except Exception as e:
                    errors.append(f"Redis cleanup failed: {str(e)}")
                    logger.warning(f"Redis session cleanup failed: {e}")
            
        except Exception as e:
            errors.append(f"General cleanup error: {str(e)}")
            logger.error(f"Session cleanup encountered error: {e}")
        
        # Calculate duration
        end_time = datetime.utcnow()
        duration = (end_time - start_time).total_seconds()
        
        # Create stats record
        stats = SessionCleanupStats(
            cleanup_time=start_time,
            expired_sessions_removed=expired_count,
            total_sessions_before=total_before,
            total_sessions_after=total_after,
            cleanup_duration_seconds=duration,
            errors=errors
        )
        
        # Store in history (keep last 100 entries)
        self.stats_history.append(stats)
        if len(self.stats_history) > 100:
            self.stats_history.pop(0)
        
        logger.info(f"Session cleanup completed in {duration:.2f}s, removed {expired_count} sessions")
        
        return stats
    
    async def _cleanup_redis_sessions(self, cutoff_time: datetime):
        """Clean up expired sessions from Redis cache."""
        redis_client = get_redis_client()
        if not redis_client:
            return
        
        try:
            # Get all session keys
            session_keys = await redis_client.keys("session:*")
            expired_keys = []
            
            for key in session_keys:
                try:
                    # Get session data
                    session_data = await redis_client.get(key)
                    if session_data:
                        import json
                        session_info = json.loads(session_data)
                        created_at = datetime.fromisoformat(session_info.get("created_at", ""))
                        
                        if created_at < cutoff_time:
                            expired_keys.append(key)
                
                except Exception as e:
                    logger.warning(f"Could not process Redis key {key}: {e}")
            
            # Delete expired keys
            if expired_keys:
                await redis_client.delete(*expired_keys)
                logger.info(f"Cleaned up {len(expired_keys)} expired Redis sessions")
        
        except Exception as e:
            logger.error(f"Redis session cleanup failed: {e}")
            raise
    
    async def get_session_statistics(self) -> Dict[str, Any]:
        """
        Get comprehensive session statistics.
        
        Returns:
            Dict containing session statistics and cleanup history
        """
        try:
            # Get current database stats
            db_stats = await UserDatabase.get_session_stats()
            
            # Get Redis stats if available
            redis_stats = {}
            if _has_redis:
                try:
                    redis_client = get_redis_client()
                    if redis_client:
                        redis_keys = await redis_client.keys("session:*")
                        redis_stats = {
                            "redis_sessions": len(redis_keys),
                            "redis_available": True
                        }
                except Exception as e:
                    redis_stats = {
                        "redis_sessions": 0,
                        "redis_available": False,
                        "redis_error": str(e)
                    }
            
            # Get cleanup history stats
            cleanup_stats = {}
            if self.stats_history:
                recent_cleanups = self.stats_history[-10:]  # Last 10 cleanups
                total_cleaned = sum(s.expired_sessions_removed for s in recent_cleanups)
                avg_duration = sum(s.cleanup_duration_seconds for s in recent_cleanups) / len(recent_cleanups)
                
                cleanup_stats = {
                    "total_cleanups": len(self.stats_history),
                    "recent_cleanups": len(recent_cleanups),
                    "total_sessions_cleaned": total_cleaned,
                    "average_cleanup_duration": round(avg_duration, 2),
                    "last_cleanup": self.stats_history[-1].cleanup_time.isoformat() if self.stats_history else None,
                    "cleanup_errors": sum(len(s.errors) for s in recent_cleanups)
                }
            
            # Combine all stats
            combined_stats = {
                "timestamp": datetime.utcnow().isoformat(),
                "database": db_stats,
                "redis": redis_stats,
                "cleanup": cleanup_stats,
                "service": {
                    "is_running": self.is_running,
                    "database_available": _has_database,
                    "redis_available": _has_redis,
                    "cleanup_interval_hours": getattr(self.settings, 'SESSION_CLEANUP_INTERVAL_HOURS', 1),
                    "session_expiry_hours": getattr(self.settings, 'SESSION_EXPIRY_HOURS', 24)
                }
            }
            
            return combined_stats
            
        except Exception as e:
            logger.error(f"Failed to get session statistics: {e}")
            return {
                "error": str(e),
                "timestamp": datetime.utcnow().isoformat(),
                "service": {
                    "is_running": self.is_running,
                    "database_available": _has_database,
                    "redis_available": _has_redis
                }
            }
    
    async def get_cleanup_history(self, limit: int = 20) -> List[Dict[str, Any]]:
        """
        Get recent cleanup operation history.
        
        Args:
            limit: Maximum number of entries to return
            
        Returns:
            List of cleanup statistics
        """
        history = self.stats_history[-limit:] if self.stats_history else []
        
        return [
            {
                "cleanup_time": stats.cleanup_time.isoformat(),
                "expired_sessions_removed": stats.expired_sessions_removed,
                "total_sessions_before": stats.total_sessions_before,
                "total_sessions_after": stats.total_sessions_after,
                "cleanup_duration_seconds": stats.cleanup_duration_seconds,
                "errors": stats.errors,
                "success": len(stats.errors) == 0
            }
            for stats in history
        ]
    
    async def start_background_cleanup(self):
        """Start the background cleanup task."""
        if self.is_running:
            logger.warning("Background cleanup already running")
            return
        
        self.is_running = True
        self.cleanup_task = asyncio.create_task(self._background_cleanup_loop())
        logger.info("Background session cleanup started")
    
    async def stop_background_cleanup(self):
        """Stop the background cleanup task."""
        if not self.is_running:
            return
        
        self.is_running = False
        if self.cleanup_task:
            self.cleanup_task.cancel()
            try:
                await self.cleanup_task
            except asyncio.CancelledError:
                pass
        
        logger.info("Background session cleanup stopped")
    
    async def _background_cleanup_loop(self):
        """Background task loop for automatic session cleanup."""
        cleanup_interval = getattr(self.settings, 'SESSION_CLEANUP_INTERVAL_HOURS', 1) * 3600  # Convert to seconds
        
        logger.info(f"Starting background cleanup loop with {cleanup_interval/3600}h interval")
        
        while self.is_running:
            try:
                await asyncio.sleep(cleanup_interval)
                
                if self.is_running:  # Check again after sleep
                    await self.cleanup_expired_sessions()
                
            except asyncio.CancelledError:
                logger.info("Background cleanup task cancelled")
                break
            except Exception as e:
                logger.error(f"Background cleanup task error: {e}")
                # Continue running even if one cleanup fails
                await asyncio.sleep(60)  # Wait 1 minute before retrying
    
    def get_service_status(self) -> Dict[str, Any]:
        """Get current service status."""
        return {
            "is_running": self.is_running,
            "database_available": _has_database,
            "redis_available": _has_redis,
            "total_cleanups_performed": len(self.stats_history),
            "last_cleanup": self.stats_history[-1].cleanup_time.isoformat() if self.stats_history else None,
            "cleanup_interval_hours": getattr(self.settings, 'SESSION_CLEANUP_INTERVAL_HOURS', 1),
            "session_expiry_hours": getattr(self.settings, 'SESSION_EXPIRY_HOURS', 24)
        }

# Global session cleanup service instance
session_cleanup_service = SessionCleanupService()

# Convenience functions for easy usage
async def cleanup_expired_sessions() -> SessionCleanupStats:
    """Clean up expired sessions."""
    return await session_cleanup_service.cleanup_expired_sessions()

async def get_session_statistics() -> Dict[str, Any]:
    """Get session statistics."""
    return await session_cleanup_service.get_session_statistics()

async def start_session_cleanup() -> None:
    """Start background session cleanup."""
    await session_cleanup_service.start_background_cleanup()

async def stop_session_cleanup() -> None:
    """Stop background session cleanup."""
    await session_cleanup_service.stop_background_cleanup()

def get_cleanup_service_status() -> Dict[str, Any]:
    """Get cleanup service status."""
    return session_cleanup_service.get_service_status()
