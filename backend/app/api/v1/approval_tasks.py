from fastapi import APIRouter
from fastapi import Depends
from fastapi import HTTPException

from app.schemas.approval_task import (
    ApprovalAction,
    ApprovalTaskResponse,
)

from app.services.approval_task_service import (
    ApprovalTaskService,
)

from app.api.service_dependencies import (
    get_approval_task_service,
)

router = APIRouter(
    prefix="/approval-tasks",
    tags=["Approval Tasks"],
)


@router.post(
    "/{approval_task_id}/approve",
    response_model=ApprovalTaskResponse,
)
def approve_task(
    approval_task_id: str,
    payload: ApprovalAction,
    service: ApprovalTaskService = Depends(
        get_approval_task_service
    ),
):

    try:
        return service.approve_task(
            approval_task_id,
            payload,
        )

    except ValueError as e:
        raise HTTPException(
            status_code=400,
            detail=str(e),
        )

@router.post(
    "/{approval_task_id}/reject",
    response_model=ApprovalTaskResponse,
)
def reject_task(
    approval_task_id: str,
    payload: ApprovalAction,
    service: ApprovalTaskService = Depends(
        get_approval_task_service
    ),
):
    try:
        return service.reject_task(
            approval_task_id,
            payload,
        )

    except ValueError as e:
        raise HTTPException(
            status_code=400,
            detail=str(e),
        )