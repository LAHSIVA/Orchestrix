from fastapi import APIRouter
from fastapi import Depends
from sqlalchemy.orm import Session

from app.api.dependencies import get_db
from app.repositories.workflow_instance_repository import (
    WorkflowInstanceRepository,
)
from app.schemas.workflow_instance import (
    WorkflowInstanceCreate,
    WorkflowInstanceResponse,
)
from app.services.workflow_instance_service import (
    WorkflowInstanceService,
)

router = APIRouter(
    prefix="/workflow-instances",
    tags=["Workflow Instances"],
)


@router.post(
    "",
    response_model=WorkflowInstanceResponse,
    status_code=201,
)
def start_workflow(
    payload: WorkflowInstanceCreate,
    db: Session = Depends(get_db),
):

    repository = WorkflowInstanceRepository(db)

    service = WorkflowInstanceService(repository)

    workflow_instance = service.start_workflow(payload)

    return workflow_instance