from datetime import datetime, timedelta
from typing import Optional, Dict, Any
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt
import hashlib
import secrets
from pydantic import BaseModel

from backend.config import settings

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/auth/login", auto_error=False)


class TokenData(BaseModel):
    username: Optional[str] = None
    role: Optional[str] = None
    tenant_id: Optional[str] = None


class UserOut(BaseModel):
    username: str
    email: str
    role: str
    tenant_id: str


def get_password_hash(password: str) -> str:
    salt = secrets.token_hex(16)
    key = hashlib.pbkdf2_hmac("sha256", password.encode("utf-8"), salt.encode("utf-8"), 100000)
    return f"{salt}:{key.hex()}"


def verify_password(plain_password: str, hashed_password: str) -> bool:
    if not hashed_password or ":" not in hashed_password:
        return False
    salt, key_hex = hashed_password.split(":", 1)
    key = hashlib.pbkdf2_hmac("sha256", plain_password.encode("utf-8"), salt.encode("utf-8"), 100000)
    return secrets.compare_digest(key.hex(), key_hex)


def create_access_token(data: Dict[str, Any], expires_delta: Optional[timedelta] = None) -> str:
    to_encode = data.copy()
    expire = datetime.utcnow() + (expires_delta or timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES))
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, settings.JWT_SECRET, algorithm=settings.JWT_ALGORITHM)


async def get_current_user(token: Optional[str] = Depends(oauth2_scheme)) -> UserOut:
    """Extract authenticated user and role; fallback to demo analyst if token not supplied."""
    if not token:
        # Default enterprise analyst identity for demo / dev environment
        return UserOut(
            username="analyst_jane",
            email="jane.doe@apexcloud.io",
            role="analyst",
            tenant_id="enterprise_demo"
        )

    try:
        payload = jwt.decode(token, settings.JWT_SECRET, algorithms=[settings.JWT_ALGORITHM])
        username: str = payload.get("sub", "")
        role: str = payload.get("role", "analyst")
        tenant_id: str = payload.get("tenant_id", "enterprise_demo")
        if not username:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token")
        return UserOut(username=username, email=f"{username}@apexcloud.io", role=role, tenant_id=tenant_id)
    except JWTError:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Could not validate credentials")


def require_role(required_role: str):
    """RBAC dependency checking user role permissions."""
    async def role_checker(current_user: UserOut = Depends(get_current_user)):
        roles_hierarchy = {"viewer": 1, "analyst": 2, "admin": 3}
        user_level = roles_hierarchy.get(current_user.role, 0)
        req_level = roles_hierarchy.get(required_role, 0)
        if user_level < req_level:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Operation requires '{required_role}' privileges."
            )
        return current_user
    return role_checker
