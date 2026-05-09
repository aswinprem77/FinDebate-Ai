from app.core.security import hash_password
from app.db.session import SessionLocal, init_db
from app.db.tables import UserTable
from app.models.user import User, UserTier


class UserStore:
    def initialize(self) -> None:
        raise NotImplementedError

    def create_user(self, email: str, password: str, tier: UserTier) -> User:
        raise NotImplementedError

    def get_by_email(self, email: str) -> User | None:
        raise NotImplementedError

    def get_by_id(self, user_id: str) -> User | None:
        raise NotImplementedError

    def update_tier(self, user_id: str, tier: UserTier) -> User:
        raise NotImplementedError


class InMemoryUserStore:
    backend_name = "memory"

    def __init__(self) -> None:
        self._users_by_id: dict[str, User] = {}
        self._user_ids_by_email: dict[str, str] = {}

    def initialize(self) -> None:
        return None

    def create_user(self, email: str, password: str, tier: UserTier) -> User:
        user = User(email=email.lower(), password_hash=hash_password(password), tier=tier)
        self._users_by_id[user.user_id] = user
        self._user_ids_by_email[user.email] = user.user_id
        return user

    def get_by_email(self, email: str) -> User | None:
        user_id = self._user_ids_by_email.get(email.lower())
        if user_id is None:
            return None
        return self._users_by_id.get(user_id)

    def get_by_id(self, user_id: str) -> User | None:
        return self._users_by_id.get(user_id)

    def update_tier(self, user_id: str, tier: UserTier) -> User:
        user = self._users_by_id[user_id]
        user.tier = tier
        return user


class PostgresUserStore(UserStore):
    backend_name = "postgresql"

    def initialize(self) -> None:
        init_db()

    def create_user(self, email: str, password: str, tier: UserTier) -> User:
        user = User(email=email.lower(), password_hash=hash_password(password), tier=tier)
        row = UserTable(
            user_id=user.user_id,
            email=user.email,
            password_hash=user.password_hash,
            tier=user.tier.value,
            created_at=user.created_at,
            rate_limit_override=user.rate_limit_override,
        )
        with SessionLocal() as session:
            session.add(row)
            session.commit()
        return user

    def get_by_email(self, email: str) -> User | None:
        with SessionLocal() as session:
            row = session.query(UserTable).filter(UserTable.email == email.lower()).one_or_none()
            return self._to_user(row) if row else None

    def get_by_id(self, user_id: str) -> User | None:
        with SessionLocal() as session:
            row = session.get(UserTable, user_id)
            return self._to_user(row) if row else None

    def update_tier(self, user_id: str, tier: UserTier) -> User:
        with SessionLocal() as session:
            row = session.get(UserTable, user_id)
            if row is None:
                raise KeyError(user_id)
            row.tier = tier.value
            session.commit()
            session.refresh(row)
            return self._to_user(row)

    def _to_user(self, row: UserTable) -> User:
        return User(
            user_id=row.user_id,
            email=row.email,
            password_hash=row.password_hash,
            tier=UserTier(row.tier),
            created_at=row.created_at,
            rate_limit_override=row.rate_limit_override,
        )


user_store: UserStore = PostgresUserStore() if SessionLocal else InMemoryUserStore()
