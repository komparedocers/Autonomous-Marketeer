"""Authentication router."""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.core.security import verify_password, get_password_hash, create_access_token
from app.models.user import User
from app.models.tenant import Tenant
from app.schemas.auth import (
    LoginRequest,
    LoginResponse,
    RegisterRequest,
    RegisterResponse,
)
from datetime import datetime

router = APIRouter()


@router.post("/login", response_model=LoginResponse)
async def login(request: LoginRequest, db: Session = Depends(get_db)):
    """Login endpoint."""
    # Find user by email
    user = db.query(User).filter(User.email == request.email).first()

    if not user or not verify_password(request.password, user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Inactive user"
        )

    # Update last login
    user.last_login = datetime.utcnow()
    db.commit()

    # Create access token
    access_token = create_access_token(
        data={"sub": str(user.id), "tenant_id": str(user.tenant_id), "role": user.role}
    )

    return LoginResponse(
        access_token=access_token,
        user_id=user.id,
        tenant_id=user.tenant_id,
        role=user.role,
    )


@router.post("/register", response_model=RegisterResponse)
async def register(request: RegisterRequest, db: Session = Depends(get_db)):
    """Registration endpoint."""
    # Check if user already exists
    existing_user = db.query(User).filter(User.email == request.email).first()
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered"
        )

    # Create new tenant
    tenant = Tenant(
        name=request.tenant_name,
        plan="free",
        status="active",
    )
    db.add(tenant)
    db.flush()  # Get tenant ID

    # Create new user
    user = User(
        tenant_id=tenant.id,
        email=request.email,
        password_hash=get_password_hash(request.password),
        first_name=request.first_name,
        last_name=request.last_name,
        role="admin",  # First user is admin
        is_active=True,
    )
    db.add(user)
    db.commit()
    db.refresh(user)

    # Create access token
    access_token = create_access_token(
        data={"sub": str(user.id), "tenant_id": str(user.tenant_id), "role": user.role}
    )

    return RegisterResponse(
        access_token=access_token,
        user_id=user.id,
        tenant_id=user.tenant_id,
    )
