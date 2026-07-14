from fastapi import APIRouter
from fastapi import Depends
from fastapi import HTTPException
from sqlalchemy.orm import Session

from app.api.dependencies import get_db
from app.repositories.workflow_definition_repository import (
    WorkflowDefinitionRepository,
)
from app.schemas.workflow_definition import (
    WorkflowDefinitionCreate,
    WorkflowDefinitionResponse,
)
from app.services.workflow_definition_service import (
    WorkflowDefinitionService,
)

router = APIRouter(
    prefix="/workflow-definitions",
    tags=["Workflow Definitions"],
)


@router.post(
    "",
    response_model=WorkflowDefinitionResponse,
    status_code=201,
)
def create_workflow_definition(
    payload: WorkflowDefinitionCreate,
    db: Session = Depends(get_db),
):

    repository = WorkflowDefinitionRepository(db)

    service = WorkflowDefinitionService(repository)

    try:
        return service.create_workflow_definition(payload)

    except ValueError as e:
        raise HTTPException(
            status_code=400,
            detail=str(e),
        )


@router.get(
    "",
    response_model=list[WorkflowDefinitionResponse],
)
def get_workflow_definitions(
    db: Session = Depends(get_db),
):

    repository = WorkflowDefinitionRepository(db)

    service = WorkflowDefinitionService(repository)

    return service.get_workflow_definitions()