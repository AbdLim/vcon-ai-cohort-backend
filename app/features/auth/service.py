from fastapi import HTTPException, status
from app.features.auth.repository import AuthRepository
from app.features.auth.schemas import UserCreate, UserLogin, Token
from app.features.auth.models import Auth
from app.features.users.models import User
from app.core.security import verify_password, create_access_token, create_refresh_token, get_password_hash
from app.infrastructure.redis import redis_client
from app.core.config import settings

class AuthService:
    def __init__(self, repository: AuthRepository):
        self.repository = repository

    async def register_user(self, user_in: UserCreate):
        existing_auth = await self.repository.get_by_email(user_in.email)
        if existing_auth:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email already registered",
            )
        
        # Create user profile
        user_profile = User(
            full_name=user_in.full_name
        )
        self.repository.session.add(user_profile)
        await self.repository.session.flush() # Get user_profile.id without committing
        
        # Create auth record
        auth_record = Auth(
            email=user_in.email,
            hashed_password=get_password_hash(user_in.password),
            user_id=user_profile.id
        )
        self.repository.session.add(auth_record)
        
        await self.repository.session.commit()
        
        # Fetch the complete record with profile loaded
        return await self.repository.get_by_id(auth_record.id)

    async def authenticate_user(self, login_data: UserLogin) -> Token:
        auth = await self.repository.get_by_email(login_data.email)
        if not auth or not verify_password(login_data.password, auth.hashed_password):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Incorrect email or password",
                headers={"WWW-Authenticate": "Bearer"},
            )
        if not auth.is_active:
             raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Inactive user",
            )

        return await self._generate_tokens(auth.id)

    async def _generate_tokens(self, auth_id: int) -> Token:
        access_token = create_access_token(auth_id)
        refresh_token = create_refresh_token()
        
        await redis_client.set(
            f"refresh_token:{refresh_token}", 
            str(auth_id), 
            expire=settings.REFRESH_TOKEN_EXPIRE_DAYS * 24 * 60 * 60
        )
        
        return Token(
            access_token=access_token,
            refresh_token=refresh_token,
            token_type="bearer",
        )

    async def refresh_token(self, refresh_token: str) -> Token:
        auth_id_str = await redis_client.get(f"refresh_token:{refresh_token}")
        if not auth_id_str:
             raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid or expired refresh token",
            )
        
        await redis_client.delete(f"refresh_token:{refresh_token}")
        return await self._generate_tokens(int(auth_id_str))

    async def logout(self, refresh_token: str) -> None:
        await redis_client.delete(f"refresh_token:{refresh_token}")
