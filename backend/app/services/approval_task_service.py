from datetime import datetime, timezone

from app.models.enums import ApprovalStatus,WorkflowStatus
from app.models.approval_task import ApprovalTask


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

        self.approval_task_repository.update(
        approval_task
        )

        workflow_instance = (
            self.workflow_instance_repository.get_by_id(
                approval_task.workflow_instance_id
            )
        )

        if workflow_instance is None:
            raise ValueError(
                "Workflow Instance does not exist."
            )

        next_step = (
        self.workflow_step_repository.get_next_step(
        workflow_definition_id=workflow_instance.workflow_definition_id,
        current_step_order=workflow_instance.current_step_order,
            )
        )

        if next_step is not None:

            # Move workflow to the next step
            workflow_instance.current_step_order = next_step.step_order

            self.workflow_instance_repository.update(
                workflow_instance
            )

            # Create the next pending approval task
            next_approval_task = ApprovalTask(
                workflow_instance_id=workflow_instance.id,
                workflow_step_id=next_step.id,

                # Temporary assignment strategy for Version 1.
                # Later this will be resolved using RBAC / approver roles.
                assigned_to=workflow_instance.initiated_by,

                status=ApprovalStatus.PENDING,
                assigned_at=datetime.now(timezone.utc),
            )

            self.approval_task_repository.create(
                next_approval_task
            )

        else:

            # There are no remaining workflow steps.
            workflow_instance.status = WorkflowStatus.COMPLETED

            workflow_instance.completed_at = datetime.now(
                timezone.utc
            )

            self.workflow_instance_repository.update(
                workflow_instance
            )

        return approval_task

        