from fastapi import APIRouter, Depends, HTTPException, status

from app.api.deps import get_current_user
from app.core.security import create_access_token, verify_password
from app.schemas.auth import (
    AuthResponse,
    LoginRequest,
    RegisterRequest,
    TierUpdateRequest,
    UserProfileResponse,
)
from app.services.user_store import user_store

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/register", response_model=AuthResponse, status_code=status.HTTP_201_CREATED)
async def register(payload: RegisterRequest):
    if user_store.get_by_email(payload.email):
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="An account already exists for this email",
        )

    user = user_store.create_user(
        email=payload.email,
        password=payload.password,
        tier=payload.tier,
    )
    token = create_access_token(subject=user.user_id)
    return AuthResponse(access_token=token, user=UserProfileResponse.from_user(user))


@router.post("/login", response_model=AuthResponse)
async def login(payload: LoginRequest):
    user = user_store.get_by_email(payload.email)
    if user is None or not verify_password(payload.password, user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    token = create_access_token(subject=user.user_id)
    return AuthResponse(access_token=token, user=UserProfileResponse.from_user(user))


@router.get("/me", response_model=UserProfileResponse)
async def me(current_user=Depends(get_current_user)):
    return UserProfileResponse.from_user(current_user)


@router.patch("/me/tier", response_model=UserProfileResponse)
async def update_tier(payload: TierUpdateRequest, current_user=Depends(get_current_user)):
    # Placeholder endpoint shape for M6. Kept intentionally narrow in M1.
    updated = user_store.update_tier(current_user.user_id, payload.tier)
    return UserProfileResponse.from_user(updated)
