from fastapi import APIRouter
from fastapi import Depends
from fastapi import HTTPException
from sqlalchemy.orm import Session

from app.api.dependencies import get_db
from app.repositories.user_repository import UserRepository
from app.schemas.user import UserCreate
from app.schemas.user import UserResponse
from app.services.user_service import UserService

router = APIRouter(
    prefix="/users",
    tags=["Users"]
)


@router.post(
    "",
    response_model=UserResponse,
    status_code=201
)
def create_user(
    payload: UserCreate,
    db: Session = Depends(get_db)
):

    repository = UserRepository(db)

    service = UserService(repository)

    try:
        return service.create_user(payload)

    except ValueError as e:
        raise HTTPException(
            status_code=400,
            detail=str(e)
        )