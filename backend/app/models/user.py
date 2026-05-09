from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import StrEnum
from uuid import uuid4


class UserTier(StrEnum):
    NEWBIE = "newbie"
    INTERMEDIATE = "intermediate"
    PRO = "pro"
    ADMIN = "admin"


@dataclass
class User:
    email: str
    password_hash: str
    tier: UserTier = UserTier.NEWBIE
    user_id: str = field(default_factory=lambda: str(uuid4()))
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    rate_limit_override: int | None = None
