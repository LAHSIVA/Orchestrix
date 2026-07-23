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

from app.schemas.workflow_audit_log import (
    WorkflowAuditLogResponse,
)
from app.services.workflow_audit_service import (
    WorkflowAuditService,
)
from app.api.service_dependencies import (
    get_workflow_audit_service,
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

@router.get(
    "/{workflow_instance_id}/audit-logs",
    response_model=list[WorkflowAuditLogResponse],
)
def get_workflow_audit_logs(
    workflow_instance_id: str,
    audit_service: WorkflowAuditService = Depends(
        get_workflow_audit_service
    ),
):
    audit_logs = audit_service.get_history(
        workflow_instance_id
    )

    if not audit_logs:
        raise HTTPException(
            status_code=404,
            detail=(
                "Workflow instance or audit "
                "history not found."
            ),
        )

    return audit_logs