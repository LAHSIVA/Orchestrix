from datetime import datetime, timezone

from app.models.enums import WorkflowStatus
from app.models.workflow_instance import WorkflowInstance
from app.repositories.workflow_instance_repository import (
    WorkflowInstanceRepository,
)
from app.schemas.workflow_instance import (
    WorkflowInstanceCreate,
)


class WorkflowInstanceService:
    """
    Business logic for workflow execution.
    """

    def __init__(
        self,
        repository: WorkflowInstanceRepository,
    ):
        self.repository = repository

    def start_workflow(
        self,
        payload: WorkflowInstanceCreate,
    ) -> WorkflowInstance:

        workflow_instance = WorkflowInstance(
            workflow_definition_id=payload.workflow_definition_id,
            initiated_by=payload.initiated_by,
            status=WorkflowStatus.IN_PROGRESS,
            current_step_order=1,
            started_at=datetime.now(timezone.utc),
        )

        return self.repository.create(workflow_instance)