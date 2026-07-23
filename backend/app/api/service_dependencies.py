from fastapi import Depends
from sqlalchemy.orm import Session

from app.api.dependencies import get_db

from app.repositories.user_repository import UserRepository
from app.repositories.workflow_definition_repository import (
    WorkflowDefinitionRepository,
)
from app.repositories.workflow_step_repository import (
    WorkflowStepRepository,
)
from app.repositories.workflow_instance_repository import (
    WorkflowInstanceRepository,
)

from app.services.workflow_instance_service import (
    WorkflowInstanceService,
)

from app.services.approval_task_service import ApprovalTaskService

from app.repositories.approval_task_repository import (
    ApprovalTaskRepository,
)

from app.services.workflow_audit_service import (
    WorkflowAuditService,
)


def get_workflow_instance_service(
    db: Session = Depends(get_db),
) -> WorkflowInstanceService:

    return WorkflowInstanceService(
        db=db,
        user_repository=UserRepository(db),
        workflow_definition_repository=WorkflowDefinitionRepository(db),
        workflow_step_repository=WorkflowStepRepository(db),
        workflow_instance_repository=WorkflowInstanceRepository(db),
        approval_task_repository=ApprovalTaskRepository(db),
    )

def get_approval_task_service(
    db: Session = Depends(get_db),
) -> ApprovalTaskService:

    return ApprovalTaskService(
        db=db,
        approval_task_repository=ApprovalTaskRepository(db),
        workflow_instance_repository=WorkflowInstanceRepository(db),
        workflow_step_repository=WorkflowStepRepository(db),
    )

def get_workflow_audit_service(
    db: Session = Depends(get_db),
) -> WorkflowAuditService:
    """
    Provide WorkflowAuditService using the
    request-scoped database session.
    """

    return WorkflowAuditService(
        db=db
    )