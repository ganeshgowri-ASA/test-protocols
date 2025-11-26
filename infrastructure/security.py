"""
Security Infrastructure for Railway Production Deployment
==========================================================
Enterprise-grade authentication, authorization, rate limiting,
and security utilities.
"""

import os
import time
import hashlib
import secrets
import threading
from datetime import datetime, timedelta
from typing import Optional, Dict, Any, List, Callable
from dataclasses import dataclass
from functools import wraps
from collections import defaultdict
import base64
import hmac
import json

try:
    import bcrypt
    BCRYPT_AVAILABLE = True
except ImportError:
    BCRYPT_AVAILABLE = False


class SecurityConfig:
    """Security configuration from environment"""

    def __init__(self):
        # JWT/Session settings
        self.secret_key = os.getenv("SESSION_SECRET_KEY", os.getenv("SECRET_KEY", secrets.token_hex(32)))
        self.token_expiry_hours = int(os.getenv("TOKEN_EXPIRY_HOURS", "24"))
        self.refresh_token_days = int(os.getenv("REFRESH_TOKEN_DAYS", "7"))

        # Rate limiting
        self.rate_limit_requests = int(os.getenv("RATE_LIMIT_REQUESTS", "100"))
        self.rate_limit_window = int(os.getenv("RATE_LIMIT_WINDOW", "60"))  # seconds

        # Password policy
        self.password_min_length = int(os.getenv("PASSWORD_MIN_LENGTH", "8"))
        self.password_require_upper = os.getenv("PASSWORD_REQUIRE_UPPER", "true").lower() == "true"
        self.password_require_lower = os.getenv("PASSWORD_REQUIRE_LOWER", "true").lower() == "true"
        self.password_require_digit = os.getenv("PASSWORD_REQUIRE_DIGIT", "true").lower() == "true"
        self.password_require_special = os.getenv("PASSWORD_REQUIRE_SPECIAL", "false").lower() == "true"

        # Session settings
        self.session_timeout_minutes = int(os.getenv("SESSION_TIMEOUT_MINUTES", "120"))
        self.max_concurrent_sessions = int(os.getenv("MAX_CONCURRENT_SESSIONS", "5"))

        # Security headers
        self.enable_cors = os.getenv("ENABLE_CORS", "true").lower() == "true"
        self.allowed_origins = os.getenv("CORS_ORIGINS", "*").split(",")

        # API key settings
        self.api_key_header = os.getenv("API_KEY_HEADER", "X-API-Key")


@dataclass
class RateLimitResult:
    """Result of a rate limit check"""
    allowed: bool
    remaining: int
    reset_time: int
    retry_after: Optional[int] = None


class RateLimiter:
    """
    Token bucket rate limiter with sliding window.

    Features:
    - Per-client rate limiting
    - Sliding window algorithm
    - Configurable limits per endpoint
    - Automatic cleanup of expired entries
    """

    def __init__(self, default_limit: int = 100, window_seconds: int = 60):
        self.default_limit = default_limit
        self.window_seconds = window_seconds
        self._buckets: Dict[str, List[float]] = defaultdict(list)
        self._lock = threading.Lock()
        self._custom_limits: Dict[str, tuple] = {}

        # Start cleanup thread
        self._cleanup_thread = threading.Thread(target=self._cleanup_loop, daemon=True)
        self._cleanup_thread.start()

    def set_limit(self, key_pattern: str, limit: int, window: int = None):
        """Set custom limit for a key pattern"""
        self._custom_limits[key_pattern] = (limit, window or self.window_seconds)

    def check(self, key: str) -> RateLimitResult:
        """
        Check if request is allowed under rate limit.

        Args:
            key: Unique identifier for the client (e.g., IP address, user ID)

        Returns:
            RateLimitResult with allowed status and remaining quota
        """
        limit, window = self._get_limit(key)
        current_time = time.time()

        with self._lock:
            # Clean old entries
            self._buckets[key] = [
                ts for ts in self._buckets[key]
                if current_time - ts < window
            ]

            # Check limit
            if len(self._buckets[key]) >= limit:
                oldest = min(self._buckets[key])
                retry_after = int(oldest + window - current_time) + 1

                return RateLimitResult(
                    allowed=False,
                    remaining=0,
                    reset_time=int(oldest + window),
                    retry_after=retry_after
                )

            # Add new request
            self._buckets[key].append(current_time)
            remaining = limit - len(self._buckets[key])

            return RateLimitResult(
                allowed=True,
                remaining=remaining,
                reset_time=int(current_time + window)
            )

    def _get_limit(self, key: str) -> tuple:
        """Get limit for a key, checking custom limits"""
        for pattern, (limit, window) in self._custom_limits.items():
            if pattern in key or key.startswith(pattern):
                return limit, window
        return self.default_limit, self.window_seconds

    def _cleanup_loop(self):
        """Periodically clean up expired entries"""
        while True:
            time.sleep(60)  # Cleanup every minute
            self._cleanup()

    def _cleanup(self):
        """Remove expired bucket entries"""
        current_time = time.time()

        with self._lock:
            empty_keys = []
            for key, timestamps in self._buckets.items():
                self._buckets[key] = [
                    ts for ts in timestamps
                    if current_time - ts < self.window_seconds
                ]
                if not self._buckets[key]:
                    empty_keys.append(key)

            for key in empty_keys:
                del self._buckets[key]

    def reset(self, key: str = None):
        """Reset rate limit for a key or all keys"""
        with self._lock:
            if key:
                self._buckets.pop(key, None)
            else:
                self._buckets.clear()

    def get_stats(self) -> Dict[str, Any]:
        """Get rate limiter statistics"""
        with self._lock:
            return {
                "active_clients": len(self._buckets),
                "total_tracked_requests": sum(len(v) for v in self._buckets.values()),
                "custom_limits": len(self._custom_limits)
            }


class PasswordManager:
    """Secure password hashing and validation"""

    def __init__(self, config: SecurityConfig = None):
        self.config = config or SecurityConfig()

    def hash_password(self, password: str) -> str:
        """Hash a password securely"""
        if BCRYPT_AVAILABLE:
            return bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode()
        else:
            # Fallback to SHA-256 with salt (less secure but works without bcrypt)
            salt = secrets.token_hex(16)
            hash_obj = hashlib.sha256((salt + password).encode())
            return f"sha256:{salt}:{hash_obj.hexdigest()}"

    def verify_password(self, password: str, hashed: str) -> bool:
        """Verify a password against its hash"""
        if BCRYPT_AVAILABLE and not hashed.startswith("sha256:"):
            try:
                return bcrypt.checkpw(password.encode(), hashed.encode())
            except Exception:
                return False
        elif hashed.startswith("sha256:"):
            _, salt, hash_value = hashed.split(":")
            hash_obj = hashlib.sha256((salt + password).encode())
            return hmac.compare_digest(hash_obj.hexdigest(), hash_value)
        return False

    def validate_password_strength(self, password: str) -> tuple:
        """
        Validate password meets security requirements.

        Returns:
            Tuple of (is_valid, list of issues)
        """
        issues = []

        if len(password) < self.config.password_min_length:
            issues.append(f"Password must be at least {self.config.password_min_length} characters")

        if self.config.password_require_upper and not any(c.isupper() for c in password):
            issues.append("Password must contain at least one uppercase letter")

        if self.config.password_require_lower and not any(c.islower() for c in password):
            issues.append("Password must contain at least one lowercase letter")

        if self.config.password_require_digit and not any(c.isdigit() for c in password):
            issues.append("Password must contain at least one digit")

        if self.config.password_require_special:
            special_chars = set('!@#$%^&*()_+-=[]{}|;:,.<>?')
            if not any(c in special_chars for c in password):
                issues.append("Password must contain at least one special character")

        return len(issues) == 0, issues

    def generate_secure_password(self, length: int = 16) -> str:
        """Generate a secure random password"""
        alphabet = "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789!@#$%^&*"
        return ''.join(secrets.choice(alphabet) for _ in range(length))


class TokenManager:
    """Secure token generation and validation"""

    def __init__(self, config: SecurityConfig = None):
        self.config = config or SecurityConfig()

    def generate_token(self, payload: Dict[str, Any], expiry_hours: int = None) -> str:
        """Generate a signed token"""
        expiry = expiry_hours or self.config.token_expiry_hours
        expires_at = datetime.utcnow() + timedelta(hours=expiry)

        token_data = {
            "payload": payload,
            "exp": expires_at.isoformat(),
            "iat": datetime.utcnow().isoformat(),
            "jti": secrets.token_hex(16)
        }

        # Encode and sign
        data_json = json.dumps(token_data, sort_keys=True)
        data_b64 = base64.urlsafe_b64encode(data_json.encode()).decode()

        signature = hmac.new(
            self.config.secret_key.encode(),
            data_b64.encode(),
            hashlib.sha256
        ).hexdigest()

        return f"{data_b64}.{signature}"

    def verify_token(self, token: str) -> Optional[Dict[str, Any]]:
        """Verify and decode a token"""
        try:
            parts = token.split(".")
            if len(parts) != 2:
                return None

            data_b64, signature = parts

            # Verify signature
            expected_signature = hmac.new(
                self.config.secret_key.encode(),
                data_b64.encode(),
                hashlib.sha256
            ).hexdigest()

            if not hmac.compare_digest(signature, expected_signature):
                return None

            # Decode payload
            data_json = base64.urlsafe_b64decode(data_b64).decode()
            token_data = json.loads(data_json)

            # Check expiry
            expires_at = datetime.fromisoformat(token_data["exp"])
            if datetime.utcnow() > expires_at:
                return None

            return token_data["payload"]

        except Exception:
            return None

    def generate_api_key(self) -> str:
        """Generate a secure API key"""
        return f"sk_{secrets.token_urlsafe(32)}"

    def generate_refresh_token(self) -> str:
        """Generate a refresh token"""
        return secrets.token_urlsafe(64)


class SecureSession:
    """
    Secure session management.

    Features:
    - Session creation and validation
    - Automatic expiry
    - Session metadata tracking
    - Multi-session support per user
    """

    def __init__(self, config: SecurityConfig = None):
        self.config = config or SecurityConfig()
        self._sessions: Dict[str, Dict] = {}
        self._user_sessions: Dict[str, List[str]] = defaultdict(list)
        self._lock = threading.Lock()

        # Start cleanup thread
        self._cleanup_thread = threading.Thread(target=self._cleanup_loop, daemon=True)
        self._cleanup_thread.start()

    def create_session(
        self,
        user_id: str,
        metadata: Dict[str, Any] = None
    ) -> str:
        """Create a new session for a user"""
        session_id = secrets.token_urlsafe(32)
        expires_at = datetime.utcnow() + timedelta(minutes=self.config.session_timeout_minutes)

        with self._lock:
            # Enforce max concurrent sessions
            user_session_ids = self._user_sessions[user_id]
            while len(user_session_ids) >= self.config.max_concurrent_sessions:
                # Remove oldest session
                old_session_id = user_session_ids.pop(0)
                self._sessions.pop(old_session_id, None)

            # Create new session
            self._sessions[session_id] = {
                "user_id": user_id,
                "created_at": datetime.utcnow().isoformat(),
                "expires_at": expires_at.isoformat(),
                "last_activity": datetime.utcnow().isoformat(),
                "metadata": metadata or {}
            }

            self._user_sessions[user_id].append(session_id)

        return session_id

    def validate_session(self, session_id: str) -> Optional[Dict[str, Any]]:
        """Validate a session and return session data"""
        with self._lock:
            session = self._sessions.get(session_id)

            if not session:
                return None

            # Check expiry
            expires_at = datetime.fromisoformat(session["expires_at"])
            if datetime.utcnow() > expires_at:
                self._invalidate_session(session_id)
                return None

            # Update last activity
            session["last_activity"] = datetime.utcnow().isoformat()

            return session

    def refresh_session(self, session_id: str) -> bool:
        """Extend session expiry"""
        with self._lock:
            session = self._sessions.get(session_id)

            if not session:
                return False

            session["expires_at"] = (
                datetime.utcnow() + timedelta(minutes=self.config.session_timeout_minutes)
            ).isoformat()
            session["last_activity"] = datetime.utcnow().isoformat()

            return True

    def invalidate_session(self, session_id: str):
        """Invalidate a session"""
        with self._lock:
            self._invalidate_session(session_id)

    def _invalidate_session(self, session_id: str):
        """Internal session invalidation (must be called with lock)"""
        session = self._sessions.pop(session_id, None)
        if session:
            user_id = session["user_id"]
            if session_id in self._user_sessions[user_id]:
                self._user_sessions[user_id].remove(session_id)

    def invalidate_user_sessions(self, user_id: str):
        """Invalidate all sessions for a user"""
        with self._lock:
            session_ids = self._user_sessions.pop(user_id, [])
            for session_id in session_ids:
                self._sessions.pop(session_id, None)

    def _cleanup_loop(self):
        """Periodically clean up expired sessions"""
        while True:
            time.sleep(300)  # Cleanup every 5 minutes
            self._cleanup()

    def _cleanup(self):
        """Remove expired sessions"""
        current_time = datetime.utcnow()

        with self._lock:
            expired = []
            for session_id, session in self._sessions.items():
                expires_at = datetime.fromisoformat(session["expires_at"])
                if current_time > expires_at:
                    expired.append(session_id)

            for session_id in expired:
                self._invalidate_session(session_id)

    def get_stats(self) -> Dict[str, Any]:
        """Get session statistics"""
        with self._lock:
            return {
                "active_sessions": len(self._sessions),
                "unique_users": len(self._user_sessions),
                "sessions_per_user": {
                    user_id: len(sessions)
                    for user_id, sessions in self._user_sessions.items()
                }
            }


class AuthenticationManager:
    """
    Complete authentication manager.

    Integrates password management, token handling, and session management.
    """

    def __init__(self, config: SecurityConfig = None):
        self.config = config or SecurityConfig()
        self.password_manager = PasswordManager(self.config)
        self.token_manager = TokenManager(self.config)
        self.session_manager = SecureSession(self.config)
        self.rate_limiter = RateLimiter(
            default_limit=self.config.rate_limit_requests,
            window_seconds=self.config.rate_limit_window
        )

    def authenticate(
        self,
        username: str,
        password: str,
        stored_hash: str,
        user_id: str,
        client_ip: str = None,
        metadata: Dict[str, Any] = None
    ) -> Optional[Dict[str, Any]]:
        """
        Authenticate a user and create a session.

        Returns:
            Authentication result with tokens and session info, or None if failed
        """
        # Rate limit check
        rate_key = f"auth:{client_ip or 'unknown'}"
        rate_result = self.rate_limiter.check(rate_key)

        if not rate_result.allowed:
            return None

        # Verify password
        if not self.password_manager.verify_password(password, stored_hash):
            return None

        # Create session
        session_id = self.session_manager.create_session(
            user_id=user_id,
            metadata={
                "username": username,
                "ip": client_ip,
                **(metadata or {})
            }
        )

        # Generate tokens
        access_token = self.token_manager.generate_token({
            "user_id": user_id,
            "username": username,
            "session_id": session_id
        })

        refresh_token = self.token_manager.generate_refresh_token()

        return {
            "user_id": user_id,
            "session_id": session_id,
            "access_token": access_token,
            "refresh_token": refresh_token,
            "expires_in": self.config.token_expiry_hours * 3600
        }

    def validate_request(
        self,
        token: str = None,
        session_id: str = None,
        api_key: str = None
    ) -> Optional[Dict[str, Any]]:
        """
        Validate an incoming request.

        Supports token-based, session-based, or API key authentication.
        """
        if token:
            payload = self.token_manager.verify_token(token)
            if payload:
                return {"type": "token", **payload}

        if session_id:
            session = self.session_manager.validate_session(session_id)
            if session:
                return {"type": "session", **session}

        # API key validation would require database lookup
        # This is a placeholder for the pattern
        if api_key and api_key.startswith("sk_"):
            # In production, validate against database
            return {"type": "api_key", "key": api_key}

        return None

    def logout(self, session_id: str):
        """Log out a session"""
        self.session_manager.invalidate_session(session_id)


# Decorators
def require_auth(func: Callable):
    """Decorator to require authentication"""
    @wraps(func)
    def wrapper(*args, **kwargs):
        # This is a pattern - actual implementation depends on framework
        # For Streamlit, check session state
        import streamlit as st

        if 'authenticated' not in st.session_state or not st.session_state.authenticated:
            st.error("Authentication required")
            st.stop()

        return func(*args, **kwargs)
    return wrapper


def rate_limit(key_func: Callable = None, limit: int = 100, window: int = 60):
    """Decorator to apply rate limiting"""
    limiter = RateLimiter(default_limit=limit, window_seconds=window)

    def decorator(func: Callable):
        @wraps(func)
        def wrapper(*args, **kwargs):
            key = key_func(*args, **kwargs) if key_func else func.__name__
            result = limiter.check(key)

            if not result.allowed:
                raise Exception(f"Rate limit exceeded. Retry after {result.retry_after} seconds")

            return func(*args, **kwargs)
        return wrapper
    return decorator


# Global instances
security_config = SecurityConfig()
rate_limiter = RateLimiter(
    default_limit=security_config.rate_limit_requests,
    window_seconds=security_config.rate_limit_window
)
auth_manager = AuthenticationManager(security_config)


# Security headers for responses
def get_security_headers() -> Dict[str, str]:
    """Get recommended security headers"""
    return {
        "X-Content-Type-Options": "nosniff",
        "X-Frame-Options": "DENY",
        "X-XSS-Protection": "1; mode=block",
        "Strict-Transport-Security": "max-age=31536000; includeSubDomains",
        "Content-Security-Policy": "default-src 'self'",
        "Referrer-Policy": "strict-origin-when-cross-origin",
        "Permissions-Policy": "geolocation=(), microphone=(), camera=()"
    }
