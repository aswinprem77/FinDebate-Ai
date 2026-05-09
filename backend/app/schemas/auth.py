from datetime import datetime

from pydantic import BaseModel, EmailStr, Field

from app.models.user import User, UserTier


class RegisterRequest(BaseModel):
    email: EmailStr
    password: str = Field(min_length=8, max_length=128)
    tier: UserTier = UserTier.NEWBIE


class LoginRequest(BaseModel):
    email: EmailStr
    password: str = Field(min_length=8, max_length=128)


class TierUpdateRequest(BaseModel):
    tier: UserTier


class UserProfileResponse(BaseModel):
    user_id: str
    email: EmailStr
    tier: UserTier
    created_at: datetime
    rate_limit_override: int | None = None

    @classmethod
    def from_user(cls, user: User) -> "UserProfileResponse":
        return cls(
            user_id=user.user_id,
            email=user.email,
            tier=user.tier,
            created_at=user.created_at,
            rate_limit_override=user.rate_limit_override,
        )


class AuthResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user: UserProfileResponse
