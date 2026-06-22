from app.models.user import User
from app.models.enums import UserStatus
from app.repositories.user_repository import UserRepository
from app.schemas.user import UserCreate


class UserService:

    def __init__(self, repository: UserRepository):
        self.repository = repository

    def create_user(self, payload: UserCreate) -> User:

        existing_user = self.repository.get_by_email(
            payload.email
        )

        if existing_user:
            raise ValueError(
                "User with this email already exists"
            )

        user = User(
            name=payload.name,
            email=payload.email,
            role=payload.role,
            status=UserStatus.ACTIVE,
        )

        return self.repository.create(user)