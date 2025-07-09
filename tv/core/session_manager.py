"""
Session Management and Connection Pooling for Kairos
Manages browser sessions, connection pooling, and resource optimization
"""

import asyncio
import logging
import threading
import time
from typing import Dict, Any, List, Optional, Set
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from contextlib import asynccontextmanager
from selenium.webdriver.remote.webdriver import WebDriver

from .browser_manager import ModernBrowserManager
from .auth_manager import AuthenticationManager
from .config_manager import ConfigManager


@dataclass
class BrowserSession:
    """Represents a browser session with metadata"""
    browser: WebDriver
    session_id: str
    created_at: datetime
    last_used: datetime
    is_authenticated: bool = False
    username: Optional[str] = None
    usage_count: int = 0
    is_busy: bool = False
    error_count: int = 0
    max_errors: int = 5
    
    def __post_init__(self):
        if not self.session_id:
            self.session_id = f"session_{int(time.time())}_{id(self)}"
            
    def is_expired(self, max_age: timedelta) -> bool:
        """Check if session is expired"""
        return datetime.now() - self.created_at > max_age
        
    def is_idle(self, max_idle: timedelta) -> bool:
        """Check if session is idle"""
        return datetime.now() - self.last_used > max_idle
        
    def is_healthy(self) -> bool:
        """Check if session is healthy"""
        return self.error_count < self.max_errors
        
    def mark_used(self):
        """Mark session as used"""
        self.last_used = datetime.now()
        self.usage_count += 1
        
    def mark_error(self):
        """Mark session as having an error"""
        self.error_count += 1
        

class SessionPool:
    """
    Pool manager for browser sessions
    """
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.logger = logging.getLogger(__name__)
        
        # Pool configuration
        self.max_pool_size = config.get('max_pool_size', 10)
        self.min_pool_size = config.get('min_pool_size', 2)
        self.max_session_age = timedelta(hours=config.get('max_session_age_hours', 2))
        self.max_idle_time = timedelta(minutes=config.get('max_idle_minutes', 30))
        self.health_check_interval = config.get('health_check_interval', 300)  # 5 minutes
        
        # Pool state
        self._sessions: Dict[str, BrowserSession] = {}
        self._available_sessions: Set[str] = set()
        self._lock = threading.RLock()
        self._shutdown_event = threading.Event()
        
        # Managers
        self.browser_manager = ModernBrowserManager(config)
        self.config_manager = ConfigManager()
        
        # Background tasks
        self._health_check_thread = None
        self._start_health_check()
        
    def _start_health_check(self):
        """Start background health check thread"""
        self._health_check_thread = threading.Thread(
            target=self._health_check_loop,
            daemon=True
        )
        self._health_check_thread.start()
        
    def _health_check_loop(self):
        """Background health check loop"""
        while not self._shutdown_event.is_set():
            try:
                self._cleanup_expired_sessions()
                self._maintain_pool_size()
                
                # Wait for next check
                self._shutdown_event.wait(self.health_check_interval)
                
            except Exception as e:
                self.logger.error(f"Health check error: {e}")
                
    def _cleanup_expired_sessions(self):
        """Clean up expired and idle sessions"""
        with self._lock:
            expired_sessions = []
            
            for session_id, session in self._sessions.items():
                if (session.is_expired(self.max_session_age) or 
                    session.is_idle(self.max_idle_time) or
                    not session.is_healthy()):
                    expired_sessions.append(session_id)
                    
            for session_id in expired_sessions:
                self._remove_session(session_id)
                
            if expired_sessions:
                self.logger.info(f"Cleaned up {len(expired_sessions)} expired sessions")
                
    def _maintain_pool_size(self):
        """Maintain minimum pool size"""
        with self._lock:
            current_size = len(self._sessions)
            
            if current_size < self.min_pool_size:
                needed = self.min_pool_size - current_size
                self.logger.info(f"Creating {needed} sessions to maintain minimum pool size")
                
                for _ in range(needed):
                    try:
                        session = self._create_session()
                        self._sessions[session.session_id] = session
                        self._available_sessions.add(session.session_id)
                    except Exception as e:
                        self.logger.error(f"Failed to create session: {e}")
                        
    def _create_session(self) -> BrowserSession:
        """Create a new browser session"""
        browser = self.browser_manager.create_browser()
        session = BrowserSession(
            browser=browser,
            session_id="",  # Will be generated in __post_init__
            created_at=datetime.now(),
            last_used=datetime.now()
        )
        
        self.logger.info(f"Created new session: {session.session_id}")
        return session
        
    def _remove_session(self, session_id: str):
        """Remove session from pool"""
        if session_id in self._sessions:
            session = self._sessions[session_id]
            
            try:
                session.browser.quit()
            except Exception as e:
                self.logger.warning(f"Error closing browser: {e}")
                
            del self._sessions[session_id]
            self._available_sessions.discard(session_id)
            
            self.logger.info(f"Removed session: {session_id}")
            
    def get_session(self, timeout: float = 30.0) -> Optional[BrowserSession]:
        """
        Get available session from pool
        
        Args:
            timeout: Timeout in seconds
            
        Returns:
            Browser session or None if timeout
        """
        start_time = time.time()
        
        while time.time() - start_time < timeout:
            with self._lock:
                # Find available session
                for session_id in list(self._available_sessions):
                    session = self._sessions.get(session_id)
                    
                    if session and session.is_healthy():
                        self._available_sessions.remove(session_id)
                        session.is_busy = True
                        session.mark_used()
                        return session
                        
                # Create new session if under limit
                if len(self._sessions) < self.max_pool_size:
                    try:
                        session = self._create_session()
                        self._sessions[session.session_id] = session
                        session.is_busy = True
                        session.mark_used()
                        return session
                    except Exception as e:
                        self.logger.error(f"Failed to create session: {e}")
                        
            # Wait before retrying
            time.sleep(0.1)
            
        self.logger.warning("Session pool timeout")
        return None
        
    def return_session(self, session: BrowserSession, had_error: bool = False):
        """
        Return session to pool
        
        Args:
            session: Session to return
            had_error: Whether session had an error
        """
        with self._lock:
            if session.session_id in self._sessions:
                session.is_busy = False
                
                if had_error:
                    session.mark_error()
                    
                if session.is_healthy():
                    self._available_sessions.add(session.session_id)
                else:
                    self._remove_session(session.session_id)
                    
    def get_pool_stats(self) -> Dict[str, Any]:
        """Get pool statistics"""
        with self._lock:
            return {
                'total_sessions': len(self._sessions),
                'available_sessions': len(self._available_sessions),
                'busy_sessions': sum(1 for s in self._sessions.values() if s.is_busy),
                'authenticated_sessions': sum(1 for s in self._sessions.values() if s.is_authenticated),
                'average_usage': sum(s.usage_count for s in self._sessions.values()) / len(self._sessions) if self._sessions else 0,
                'max_pool_size': self.max_pool_size,
                'min_pool_size': self.min_pool_size
            }
            
    def shutdown(self):
        """Shutdown the session pool"""
        self.logger.info("Shutting down session pool")
        
        # Stop health check
        self._shutdown_event.set()
        if self._health_check_thread:
            self._health_check_thread.join(timeout=5)
            
        # Close all sessions
        with self._lock:
            for session_id in list(self._sessions.keys()):
                self._remove_session(session_id)
                
        self.logger.info("Session pool shutdown complete")


class SessionManager:
    """
    High-level session management
    """
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.logger = logging.getLogger(__name__)
        self.session_pool = SessionPool(config)
        
    @asynccontextmanager
    async def get_session(self):
        """
        Context manager for getting a session
        
        Usage:
            async with session_manager.get_session() as session:
                # Use session.browser
                pass
        """
        session = self.session_pool.get_session()
        if not session:
            raise RuntimeError("Failed to get session from pool")
            
        had_error = False
        try:
            yield session
        except Exception as e:
            had_error = True
            self.logger.error(f"Session error: {e}")
            raise
        finally:
            self.session_pool.return_session(session, had_error)
            
    async def get_authenticated_session(self, username: str, password: str):
        """
        Get authenticated session
        
        Args:
            username: TradingView username
            password: TradingView password
            
        Yields:
            Authenticated browser session
        """
        async with self.get_session() as session:
            if not session.is_authenticated or session.username != username:
                # Authenticate session
                auth_manager = AuthenticationManager(self.config, session.browser)
                success = auth_manager.login(username, password)
                
                if success:
                    session.is_authenticated = True
                    session.username = username
                    self.logger.info(f"Session authenticated for user: {username}")
                else:
                    raise RuntimeError("Authentication failed")
                    
            yield session
            
    async def execute_with_session(self, func, *args, **kwargs):
        """
        Execute function with session
        
        Args:
            func: Function to execute
            *args: Function arguments
            **kwargs: Function keyword arguments
            
        Returns:
            Function result
        """
        async with self.get_session() as session:
            return await func(session, *args, **kwargs)
            
    async def execute_with_auth(self, func, username: str, password: str, *args, **kwargs):
        """
        Execute function with authenticated session
        
        Args:
            func: Function to execute
            username: TradingView username
            password: TradingView password
            *args: Function arguments
            **kwargs: Function keyword arguments
            
        Returns:
            Function result
        """
        async with self.get_authenticated_session(username, password) as session:
            return await func(session, *args, **kwargs)
            
    def get_stats(self) -> Dict[str, Any]:
        """Get session manager statistics"""
        return self.session_pool.get_pool_stats()
        
    def shutdown(self):
        """Shutdown session manager"""
        self.session_pool.shutdown()


class ConnectionPool:
    """
    Connection pool for HTTP requests
    """
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.logger = logging.getLogger(__name__)
        
        # Connection pool settings
        self.max_connections = config.get('max_connections', 20)
        self.max_keepalive_connections = config.get('max_keepalive_connections', 5)
        self.keepalive_expiry = config.get('keepalive_expiry', 300)  # 5 minutes
        
        # Connection pool (would use aiohttp.ClientSession in real implementation)
        self._connection_pool = None
        self._initialize_pool()
        
    def _initialize_pool(self):
        """Initialize connection pool"""
        try:
            import aiohttp
            
            connector = aiohttp.TCPConnector(
                limit=self.max_connections,
                limit_per_host=self.max_keepalive_connections,
                keepalive_timeout=self.keepalive_expiry,
                enable_cleanup_closed=True
            )
            
            self._connection_pool = aiohttp.ClientSession(
                connector=connector,
                timeout=aiohttp.ClientTimeout(total=30)
            )
            
            self.logger.info("HTTP connection pool initialized")
            
        except ImportError:
            self.logger.warning("aiohttp not available, HTTP pool disabled")
            
    async def get_session(self):
        """Get HTTP session from pool"""
        if self._connection_pool:
            return self._connection_pool
        else:
            raise RuntimeError("HTTP connection pool not available")
            
    async def close(self):
        """Close connection pool"""
        if self._connection_pool:
            await self._connection_pool.close()
            self.logger.info("HTTP connection pool closed")


class ResourceManager:
    """
    Overall resource management
    """
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.logger = logging.getLogger(__name__)
        self.session_manager = SessionManager(config)
        self.connection_pool = ConnectionPool(config)
        
    async def __aenter__(self):
        """Async context manager entry"""
        return self
        
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit"""
        await self.shutdown()
        
    async def get_browser_session(self):
        """Get browser session"""
        return self.session_manager.get_session()
        
    async def get_http_session(self):
        """Get HTTP session"""
        return await self.connection_pool.get_session()
        
    async def get_authenticated_session(self, username: str, password: str):
        """Get authenticated browser session"""
        return self.session_manager.get_authenticated_session(username, password)
        
    def get_resource_stats(self) -> Dict[str, Any]:
        """Get resource usage statistics"""
        return {
            'browser_sessions': self.session_manager.get_stats(),
            'timestamp': datetime.now().isoformat()
        }
        
    async def shutdown(self):
        """Shutdown all resources"""
        self.logger.info("Shutting down resource manager")
        
        # Shutdown session manager
        self.session_manager.shutdown()
        
        # Close connection pool
        await self.connection_pool.close()
        
        self.logger.info("Resource manager shutdown complete")