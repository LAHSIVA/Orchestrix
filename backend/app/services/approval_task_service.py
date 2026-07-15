from datetime import datetime, timezone

from app.models.enums import ApprovalStatus

from app.repositories.approval_task_repository import ApprovalTaskRepository
from app.repositories.workflow_instance_repository import WorkflowInstanceRepository
from app.repositories.workflow_step_repository import WorkflowStepRepository

from app.schemas.approval_task import ApprovalAction


class ApprovalTaskService:

    def __init__(
        self,
        approval_task_repository: ApprovalTaskRepository,
        workflow_instance_repository: WorkflowInstanceRepository,
        workflow_step_repository: WorkflowStepRepository,
    ):
        self.approval_task_repository = approval_task_repository

        self.workflow_instance_repository = workflow_instance_repository

        self.workflow_step_repository = workflow_step_repository

    def approve_task(
        self,
        approval_task_id: str,
        payload: ApprovalAction,
    ):

        approval_task = (
            self.approval_task_repository.get_by_id(
                approval_task_id
            )
        )

        if approval_task is None:
            raise ValueError(
                "Approval Task does not exist."
            )

        if approval_task.status != ApprovalStatus.PENDING:
            raise ValueError(
                "Approval Task has already been processed."
            )

        approval_task.status = ApprovalStatus.APPROVED

        approval_task.comments = payload.comments

        approval_task.completed_at = datetime.now(
            timezone.utc
        )

        return self.approval_task_repository.update(
            approval_task
        )