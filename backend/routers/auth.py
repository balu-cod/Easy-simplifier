from fastapi import APIRouter, Depends, HTTPException, status, BackgroundTasks
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session
from datetime import timedelta
import pyotp
import qrcode
import io
import base64

from database.postgresql import get_db
from models.user import User
from schemas.user import (
    UserCreate, UserLogin, UserResponse, Token, PasswordReset, 
    PasswordResetConfirm, TwoFactorSetup, TwoFactorVerify, SocialAuthRequest
)
from services.auth_service import AuthService
from services.email_service import EmailService
from middleware.auth import get_current_user, get_current_active_user
from config.settings import settings

router = APIRouter()
security = HTTPBearer()
auth_service = AuthService()
email_service = EmailService()

@router.post("/register", response_model=UserResponse)
async def register(
    user_data: UserCreate, 
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db)
):
    """Register a new user"""
    # Check if user already exists
    existing_user = db.query(User).filter(
        (User.email == user_data.email) | (User.username == user_data.username)
    ).first()
    
    if existing_user:
        if existing_user.email == user_data.email:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email already registered"
            )
        else:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Username already taken"
            )
    
    # Create new user
    hashed_password = auth_service.get_password_hash(user_data.password)
    db_user = User(
        email=user_data.email,
        username=user_data.username,
        full_name=user_data.full_name,
        hashed_password=hashed_password
    )
    
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    
    # Send verification email
    verification_token = auth_service.create_verification_token(db_user.email)
    background_tasks.add_task(
        email_service.send_verification_email, 
        db_user.email, 
        verification_token
    )
    
    return UserResponse.model_validate(db_user)

@router.post("/login", response_model=Token)
async def login(user_data: UserLogin, db: Session = Depends(get_db)):
    """Authenticate user and return access token"""
    user = auth_service.authenticate_user(db, user_data.email, user_data.password)
    if not user:
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
    from datetime import datetime
    user.last_login = datetime.utcnow()
    db.commit()
    
    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = auth_service.create_access_token(
        data={"sub": user.email}, expires_delta=access_token_expires
    )
    
    return Token(
        access_token=access_token,
        expires_in=settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60,
        user=UserResponse.model_validate(user)
    )

@router.get("/me", response_model=UserResponse)
async def get_current_user_info(
    current_user: User = Depends(get_current_active_user)
):
    """Get current user information"""
    return UserResponse.model_validate(current_user)

@router.post("/verify-email")
async def verify_email(token: str, db: Session = Depends(get_db)):
    """Verify user email with token"""
    email = auth_service.verify_token(token)
    if not email:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid or expired verification token"
        )
    
    user = db.query(User).filter(User.email == email).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    user.is_verified = True
    db.commit()
    
    return {"message": "Email verified successfully"}

@router.post("/forgot-password")
async def forgot_password(
    password_reset: PasswordReset,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db)
):
    """Send password reset email"""
    user = db.query(User).filter(User.email == password_reset.email).first()
    if user:
        reset_token = auth_service.create_reset_token(user.email)
        background_tasks.add_task(
            email_service.send_password_reset_email,
            user.email,
            reset_token
        )
    
    return {"message": "If the email exists, a password reset link has been sent"}

@router.post("/reset-password")
async def reset_password(
    password_reset: PasswordResetConfirm,
    db: Session = Depends(get_db)
):
    """Reset password with token"""
    email = auth_service.verify_token(password_reset.token)
    if not email:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid or expired reset token"
        )
    
    user = db.query(User).filter(User.email == email).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    user.hashed_password = auth_service.get_password_hash(password_reset.new_password)
    db.commit()
    
    return {"message": "Password reset successfully"}

@router.post("/2fa/setup", response_model=TwoFactorSetup)
async def setup_2fa(
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Setup two-factor authentication"""
    secret = pyotp.random_base32()
    totp = pyotp.TOTP(secret)
    
    # Generate QR code
    provisioning_uri = totp.provisioning_uri(
        current_user.email,
        issuer_name="AI Image Processor"
    )
    
    qr = qrcode.QRCode(version=1, box_size=10, border=5)
    qr.add_data(provisioning_uri)
    qr.make(fit=True)
    
    img = qr.make_image(fill_color="black", back_color="white")
    img_buffer = io.BytesIO()
    img.save(img_buffer, format='PNG')
    img_str = base64.b64encode(img_buffer.getvalue()).decode()
    
    current_user.two_factor_secret = secret
    db.commit()
    
    return TwoFactorSetup(
        secret=secret,
        qr_code=f"data:image/png;base64,{img_str}"
    )

@router.post("/2fa/verify")
async def verify_2fa(
    verify_data: TwoFactorVerify,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Verify and enable two-factor authentication"""
    if not current_user.two_factor_secret:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="2FA not set up"
        )
    
    totp = pyotp.TOTP(current_user.two_factor_secret)
    if not totp.verify(verify_data.token):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid 2FA token"
        )
    
    current_user.two_factor_enabled = True
    db.commit()
    
    return {"message": "2FA enabled successfully"}

@router.delete("/2fa/disable")
async def disable_2fa(
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Disable two-factor authentication"""
    current_user.two_factor_enabled = False
    current_user.two_factor_secret = None
    db.commit()
    
    return {"message": "2FA disabled successfully"}

@router.post("/social/{provider}")
async def social_auth(
    provider: str,
    auth_data: SocialAuthRequest,
    db: Session = Depends(get_db)
):
    """Social authentication (Google, Facebook, GitHub)"""
    try:
        user_info = await auth_service.verify_social_token(provider, auth_data.code, auth_data.redirect_uri)
        
        # Check if user exists
        social_id_field = f"{provider}_id"
        user = db.query(User).filter(getattr(User, social_id_field) == user_info['id']).first()
        
        if not user:
            # Check by email
            user = db.query(User).filter(User.email == user_info['email']).first()
            if user:
                # Link social account
                setattr(user, social_id_field, user_info['id'])
            else:
                # Create new user
                user = User(
                    email=user_info['email'],
                    username=user_info.get('username', user_info['email'].split('@')[0]),
                    full_name=user_info.get('name'),
                    is_verified=True,
                    hashed_password=auth_service.get_password_hash("social_auth_no_password"),
                    **{social_id_field: user_info['id']}
                )
                db.add(user)
        
        db.commit()
        db.refresh(user)
        
        # Create access token
        access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
        access_token = auth_service.create_access_token(
            data={"sub": user.email}, expires_delta=access_token_expires
        )
        
        return Token(
            access_token=access_token,
            expires_in=settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60,
            user=UserResponse.model_validate(user)
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Social authentication failed: {str(e)}"
        )

@router.post("/logout")
async def logout(current_user: User = Depends(get_current_active_user)):
    """Logout user (client should remove token)"""
    return {"message": "Logged out successfully"}