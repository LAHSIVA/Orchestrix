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

from app.repositories.approval_task_repository import (
    ApprovalTaskRepository,
)


def get_workflow_instance_service(
    db: Session = Depends(get_db),
) -> WorkflowInstanceService:

    return WorkflowInstanceService(
        user_repository=UserRepository(db),
        workflow_definition_repository=WorkflowDefinitionRepository(db),
        workflow_step_repository=WorkflowStepRepository(db),
        workflow_instance_repository=WorkflowInstanceRepository(db),
        approval_task_repository=ApprovalTaskRepository(db),
    )