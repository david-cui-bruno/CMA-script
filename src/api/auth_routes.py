"""
Authentication API routes
"""
from fastapi import APIRouter, HTTPException, Depends, status
from fastapi.security import HTTPBearer
from sqlalchemy.orm import Session
from pydantic import BaseModel, EmailStr
from typing import Optional
from datetime import timedelta
from data.database import get_db
from core.auth import AuthService, get_current_user, ACCESS_TOKEN_EXPIRE_MINUTES
from models.database import User

router = APIRouter()
security = HTTPBearer()

# Pydantic models for request/response
class UserRegister(BaseModel):
    email: EmailStr
    password: str
    full_name: str
    company: Optional[str] = None
    phone: Optional[str] = None

class UserLogin(BaseModel):
    email: EmailStr
    password: str

class Token(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"

class UserResponse(BaseModel):
    id: int
    email: str
    full_name: str
    company: Optional[str]
    phone: Optional[str]
    is_active: bool
    created_at: str

    class Config:
        from_attributes = True

class PasswordChange(BaseModel):
    current_password: str
    new_password: str

@router.post("/register", response_model=UserResponse)
async def register_user(user_data: UserRegister, db: Session = Depends(get_db)):
    """Register a new user"""
    
    # Check if user already exists
    existing_user = db.query(User).filter(User.email == user_data.email).first()
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered"
        )
    
    # Validate password strength
    if len(user_data.password) < 8:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Password must be at least 8 characters long"
        )
    
    # Create new user
    hashed_password = AuthService.get_password_hash(user_data.password)
    
    db_user = User(
        email=user_data.email,
        full_name=user_data.full_name,
        company=user_data.company,
        phone=user_data.phone,
        hashed_password=hashed_password,
        is_active=True,
        is_verified=True  # Auto-verify for simplicity
    )
    
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    
    return UserResponse(
        id=db_user.id,
        email=db_user.email,
        full_name=db_user.full_name,
        company=db_user.company,
        phone=db_user.phone,
        is_active=db_user.is_active,
        created_at=db_user.created_at.isoformat()
    )

@router.post("/login", response_model=Token)
async def login_user(user_credentials: UserLogin, db: Session = Depends(get_db)):
    """Authenticate user and return JWT tokens"""
    
    # Get user from database
    user = db.query(User).filter(User.email == user_credentials.email).first()
    
    if not user or not AuthService.verify_password(user_credentials.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Inactive user account"
        )
    
    # Create tokens
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = AuthService.create_access_token(
        data={"sub": user.email, "user_id": user.id},
        expires_delta=access_token_expires
    )
    refresh_token = AuthService.create_refresh_token(
        data={"sub": user.email, "user_id": user.id}
    )
    
    return {
        "access_token": access_token,
        "refresh_token": refresh_token,
        "token_type": "bearer"
    }

@router.post("/refresh", response_model=Token)
async def refresh_token(refresh_token: str, db: Session = Depends(get_db)):
    """Refresh access token using refresh token"""
    
    try:
        # Verify refresh token
        payload = AuthService.verify_token(refresh_token)
        
        # Check token type
        if payload.get("type") != "refresh":
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid token type"
            )
        
        # Get user
        email = payload.get("sub")
        user = db.query(User).filter(User.email == email).first()
        
        if not user or not user.is_active:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="User not found or inactive"
            )
        
        # Create new tokens
        access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
        new_access_token = AuthService.create_access_token(
            data={"sub": user.email, "user_id": user.id},
            expires_delta=access_token_expires
        )
        new_refresh_token = AuthService.create_refresh_token(
            data={"sub": user.email, "user_id": user.id}
        )
        
        return {
            "access_token": new_access_token,
            "refresh_token": new_refresh_token,
            "token_type": "bearer"
        }
        
    except Exception:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid refresh token"
        )

@router.get("/me", response_model=UserResponse)
async def get_current_user_profile(current_user: User = Depends(get_current_user)):
    """Get current user profile"""
    return UserResponse(
        id=current_user.id,
        email=current_user.email,
        full_name=current_user.full_name,
        company=current_user.company,
        phone=current_user.phone,
        is_active=current_user.is_active,
        created_at=current_user.created_at.isoformat()
    )

@router.put("/me", response_model=UserResponse)
async def update_user_profile(
    user_data: UserRegister,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Update current user profile"""
    
    # Update user fields
    current_user.full_name = user_data.full_name
    current_user.company = user_data.company
    current_user.phone = user_data.phone
    
    # If password is provided, update it
    if user_data.password:
        if len(user_data.password) < 8:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Password must be at least 8 characters long"
            )
        current_user.hashed_password = AuthService.get_password_hash(user_data.password)
    
    db.commit()
    db.refresh(current_user)
    
    return UserResponse(
        id=current_user.id,
        email=current_user.email,
        full_name=current_user.full_name,
        company=current_user.company,
        phone=current_user.phone,
        is_active=current_user.is_active,
        created_at=current_user.created_at.isoformat()
    )

@router.post("/change-password")
async def change_password(
    password_data: PasswordChange,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Change user password"""
    
    # Verify current password
    if not AuthService.verify_password(password_data.current_password, current_user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Incorrect current password"
        )
    
    # Validate new password
    if len(password_data.new_password) < 8:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="New password must be at least 8 characters long"
        )
    
    # Update password
    current_user.hashed_password = AuthService.get_password_hash(password_data.new_password)
    db.commit()
    
    return {"message": "Password updated successfully"} 