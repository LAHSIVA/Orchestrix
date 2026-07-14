from fastapi import APIRouter
from fastapi import Depends
from fastapi import HTTPException
from sqlalchemy.orm import Session

from app.api.dependencies import get_db
from app.repositories.workflow_step_repository import WorkflowStepRepository
from app.schemas.workflow_step import (
    WorkflowStepCreate,
    WorkflowStepResponse,
)
from app.services.workflow_step_service import WorkflowStepService

router = APIRouter(
    prefix="/workflow-steps",
    tags=["Workflow Steps"],
)


@router.post(
    "",
    response_model=WorkflowStepResponse,
    status_code=201,
)
def create_workflow_step(
    payload: WorkflowStepCreate,
    db: Session = Depends(get_db),
):

    repository = WorkflowStepRepository(db)

    service = WorkflowStepService(repository)

    try:
        return service.create_workflow_step(payload)

    except ValueError as e:
        raise HTTPException(
            status_code=400,
            detail=str(e),
        )


@router.get(
    "/{workflow_definition_id}",
    response_model=list[WorkflowStepResponse],
)
def get_workflow_steps(
    workflow_definition_id: str,
    db: Session = Depends(get_db),
):

    repository = WorkflowStepRepository(db)

    service = WorkflowStepService(repository)

    return service.get_workflow_steps(
        workflow_definition_id
    )