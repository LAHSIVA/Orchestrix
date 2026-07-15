from fastapi import APIRouter
from fastapi import Depends
from fastapi import HTTPException

from app.api.service_dependencies import (
    get_workflow_instance_service,
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
    service: WorkflowInstanceService = Depends(
        get_workflow_instance_service
    ),
):

    try:
        return service.start_workflow(payload)

    except ValueError as e:
        raise HTTPException(
            status_code=400,
            detail=str(e),
        )