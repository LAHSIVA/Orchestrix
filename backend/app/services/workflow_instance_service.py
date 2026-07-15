from datetime import datetime, timezone

from app.models.enums import WorkflowStatus
from app.models.workflow_instance import WorkflowInstance
from app.models.approval_task import ApprovalTask
from app.models.enums import ApprovalStatus

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

from app.schemas.workflow_instance import WorkflowInstanceCreate

from app.repositories.approval_task_repository import (
    ApprovalTaskRepository,
)


class WorkflowInstanceService:

    def __init__(
        self,
        user_repository: UserRepository,
        workflow_definition_repository: WorkflowDefinitionRepository,
        workflow_step_repository: WorkflowStepRepository,
        workflow_instance_repository: WorkflowInstanceRepository,
        approval_task_repository: ApprovalTaskRepository,
    ):
        self.user_repository = user_repository
        self.workflow_definition_repository = (
            workflow_definition_repository
        )
        self.workflow_step_repository = workflow_step_repository
        self.workflow_instance_repository = (
            workflow_instance_repository
        )
        self.approval_task_repository = approval_task_repository

    def start_workflow(
        self,
        payload: WorkflowInstanceCreate,
    ) -> WorkflowInstance:

        # Validate User
        user = self.user_repository.get_by_id(
            payload.initiated_by
        )

        if not user:
            raise ValueError(
                "Initiating user does not exist."
            )

        # Validate Workflow Definition
        workflow_definition = (
            self.workflow_definition_repository.get_by_id(
                payload.workflow_definition_id
            )
        )

        if not workflow_definition:
            raise ValueError(
                "Workflow Definition does not exist."
            )

        # Validate Workflow Active
        if not workflow_definition.is_active:
            raise ValueError(
                "Workflow Definition is inactive."
            )

        # Validate Workflow Steps
        workflow_steps = (
            self.workflow_step_repository
            .get_by_workflow_definition(
                payload.workflow_definition_id
            )
        )

        if len(workflow_steps) == 0:
            raise ValueError(
                "Workflow contains no steps."
            )

        workflow_instance = WorkflowInstance(
        workflow_definition_id=payload.workflow_definition_id,
        initiated_by=payload.initiated_by,
        status=WorkflowStatus.IN_PROGRESS,
        current_step_order=1,
        started_at=datetime.now(timezone.utc),
        )
        workflow_instance = self.workflow_instance_repository.create(
        workflow_instance
        )

        first_step = workflow_steps[0]

        approval_task = ApprovalTask(
            workflow_instance_id=workflow_instance.id,
            workflow_step_id=first_step.id,

            # Temporary assignment for Version 1
            assigned_to=payload.initiated_by,

            status=ApprovalStatus.PENDING,

            assigned_at=datetime.now(timezone.utc),
        )

        self.approval_task_repository.create(
            approval_task
        )

        return workflow_instance        