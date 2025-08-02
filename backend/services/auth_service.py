from datetime import datetime, timedelta
from typing import Optional, Dict, Any
import jwt
from passlib.context import CryptContext
from sqlalchemy.orm import Session
import httpx
import secrets
import string

from models.user import User
from config.settings import settings

class AuthService:
    def __init__(self):
        self.pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
        self.secret_key = settings.SECRET_KEY
        self.algorithm = settings.ALGORITHM
        self.access_token_expire_minutes = settings.ACCESS_TOKEN_EXPIRE_MINUTES

    def verify_password(self, plain_password: str, hashed_password: str) -> bool:
        """Verify a password against its hash"""
        return self.pwd_context.verify(plain_password, hashed_password)

    def get_password_hash(self, password: str) -> str:
        """Hash a password"""
        return self.pwd_context.hash(password)

    def authenticate_user(self, db: Session, email: str, password: str) -> Optional[User]:
        """Authenticate a user by email and password"""
        user = db.query(User).filter(User.email == email).first()
        if not user:
            return None
        if not self.verify_password(password, user.hashed_password):
            return None
        return user

    def create_access_token(self, data: Dict[str, Any], expires_delta: Optional[timedelta] = None) -> str:
        """Create a JWT access token"""
        to_encode = data.copy()
        if expires_delta:
            expire = datetime.utcnow() + expires_delta
        else:
            expire = datetime.utcnow() + timedelta(minutes=self.access_token_expire_minutes)
        
        to_encode.update({"exp": expire, "iat": datetime.utcnow()})
        encoded_jwt = jwt.encode(to_encode, self.secret_key, algorithm=self.algorithm)
        return encoded_jwt

    def verify_token(self, token: str) -> Optional[str]:
        """Verify and decode a JWT token"""
        try:
            payload = jwt.decode(token, self.secret_key, algorithms=[self.algorithm])
            email: str = payload.get("sub")
            if email is None:
                return None
            return email
        except jwt.PyJWTError:
            return None

    def create_verification_token(self, email: str) -> str:
        """Create a verification token for email verification"""
        data = {"sub": email, "type": "verification"}
        expires_delta = timedelta(hours=24)  # 24 hours for email verification
        return self.create_access_token(data, expires_delta)

    def create_reset_token(self, email: str) -> str:
        """Create a password reset token"""
        data = {"sub": email, "type": "reset"}
        expires_delta = timedelta(hours=1)  # 1 hour for password reset
        return self.create_access_token(data, expires_delta)

    def generate_random_password(self, length: int = 12) -> str:
        """Generate a random password for social auth users"""
        characters = string.ascii_letters + string.digits + "!@#$%^&*"
        return ''.join(secrets.choice(characters) for _ in range(length))

    async def verify_social_token(self, provider: str, code: str, redirect_uri: str) -> Dict[str, Any]:
        """Verify social authentication token and get user info"""
        if provider == "google":
            return await self._verify_google_token(code, redirect_uri)
        elif provider == "facebook":
            return await self._verify_facebook_token(code, redirect_uri)
        elif provider == "github":
            return await self._verify_github_token(code, redirect_uri)
        else:
            raise ValueError(f"Unsupported provider: {provider}")

    async def _verify_google_token(self, code: str, redirect_uri: str) -> Dict[str, Any]:
        """Verify Google OAuth token"""
        async with httpx.AsyncClient() as client:
            # Exchange code for access token
            token_response = await client.post(
                "https://oauth2.googleapis.com/token",
                data={
                    "client_id": settings.GOOGLE_CLIENT_ID,
                    "client_secret": settings.GOOGLE_CLIENT_SECRET,
                    "code": code,
                    "grant_type": "authorization_code",
                    "redirect_uri": redirect_uri,
                }
            )
            token_data = token_response.json()
            
            if "access_token" not in token_data:
                raise ValueError("Failed to get access token from Google")
            
            # Get user info
            user_response = await client.get(
                "https://www.googleapis.com/oauth2/v2/userinfo",
                headers={"Authorization": f"Bearer {token_data['access_token']}"}
            )
            user_data = user_response.json()
            
            return {
                "id": user_data["id"],
                "email": user_data["email"],
                "name": user_data.get("name"),
                "username": user_data.get("email", "").split("@")[0],
            }

    async def _verify_facebook_token(self, code: str, redirect_uri: str) -> Dict[str, Any]:
        """Verify Facebook OAuth token"""
        async with httpx.AsyncClient() as client:
            # Exchange code for access token
            token_response = await client.get(
                "https://graph.facebook.com/v18.0/oauth/access_token",
                params={
                    "client_id": settings.FACEBOOK_APP_ID,
                    "client_secret": settings.FACEBOOK_APP_SECRET,
                    "code": code,
                    "redirect_uri": redirect_uri,
                }
            )
            token_data = token_response.json()
            
            if "access_token" not in token_data:
                raise ValueError("Failed to get access token from Facebook")
            
            # Get user info
            user_response = await client.get(
                "https://graph.facebook.com/me",
                params={
                    "fields": "id,name,email",
                    "access_token": token_data["access_token"]
                }
            )
            user_data = user_response.json()
            
            return {
                "id": user_data["id"],
                "email": user_data.get("email"),
                "name": user_data.get("name"),
                "username": user_data.get("name", "").replace(" ", "").lower(),
            }

    async def _verify_github_token(self, code: str, redirect_uri: str) -> Dict[str, Any]:
        """Verify GitHub OAuth token"""
        async with httpx.AsyncClient() as client:
            # Exchange code for access token
            token_response = await client.post(
                "https://github.com/login/oauth/access_token",
                data={
                    "client_id": settings.GITHUB_CLIENT_ID,
                    "client_secret": settings.GITHUB_CLIENT_SECRET,
                    "code": code,
                },
                headers={"Accept": "application/json"}
            )
            token_data = token_response.json()
            
            if "access_token" not in token_data:
                raise ValueError("Failed to get access token from GitHub")
            
            # Get user info
            user_response = await client.get(
                "https://api.github.com/user",
                headers={"Authorization": f"Bearer {token_data['access_token']}"}
            )
            user_data = user_response.json()
            
            # Get primary email
            email_response = await client.get(
                "https://api.github.com/user/emails",
                headers={"Authorization": f"Bearer {token_data['access_token']}"}
            )
            emails = email_response.json()
            primary_email = next((email["email"] for email in emails if email["primary"]), None)
            
            return {
                "id": str(user_data["id"]),
                "email": primary_email,
                "name": user_data.get("name"),
                "username": user_data.get("login"),
            }

    def create_2fa_secret(self) -> str:
        """Generate a new 2FA secret"""
        import pyotp
        return pyotp.random_base32()

    def verify_2fa_token(self, secret: str, token: str) -> bool:
        """Verify a 2FA token"""
        import pyotp
        totp = pyotp.TOTP(secret)
        return totp.verify(token)