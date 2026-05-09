from app.db.session import SessionLocal
from app.db.tables import RateLimitEventTable
from app.models.user import User


class RateLimitLogger:
    def log_block(
        self,
        *,
        user: User,
        route: str,
        limit_type: str,
        limit_value: int,
        observed_count: int,
    ) -> None:
        if SessionLocal is None:
            return

        with SessionLocal() as session:
            session.add(
                RateLimitEventTable(
                    user_id=user.user_id,
                    user_tier=user.tier.value,
                    route=route,
                    limit_type=limit_type,
                    limit_value=limit_value,
                    observed_count=observed_count,
                )
            )
            session.commit()


rate_limit_logger = RateLimitLogger()
