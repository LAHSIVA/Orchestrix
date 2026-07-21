from datetime import datetime, timezone
from sqlalchemy.orm import Session
from app.models.enums import ApprovalStatus,WorkflowStatus
from app.models.approval_task import ApprovalTask
from app.schemas.approval_task import ApprovalAction

from app.repositories.approval_task_repository import ApprovalTaskRepository
from app.repositories.workflow_instance_repository import WorkflowInstanceRepository
from app.repositories.workflow_step_repository import WorkflowStepRepository

from app.schemas.approval_task import ApprovalAction


class ApprovalTaskService:

    def __init__(
        self,
        db: Session,
        approval_task_repository: ApprovalTaskRepository,
        workflow_instance_repository: WorkflowInstanceRepository,
        workflow_step_repository: WorkflowStepRepository,
    ):
        self.db = db
        self.approval_task_repository = approval_task_repository
        self.workflow_instance_repository = workflow_instance_repository
        self.workflow_step_repository = workflow_step_repository

    def approve_task(
    self,
    approval_task_id: str,
    payload: ApprovalAction,
    ):
        try:
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

            # Update current task in memory
            approval_task.status = ApprovalStatus.APPROVED
            approval_task.comments = payload.comments
            approval_task.completed_at = datetime.now(
                timezone.utc
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
                    workflow_definition_id=(
                        workflow_instance.workflow_definition_id
                    ),
                    current_step_order=(
                        workflow_instance.current_step_order
                    ),
                )
            )

            if next_step is not None:

                workflow_instance.current_step_order = (
                    next_step.step_order
                )

                next_approval_task = ApprovalTask(
                    workflow_instance_id=workflow_instance.id,
                    workflow_step_id=next_step.id,
                    assigned_to=workflow_instance.initiated_by,
                    status=ApprovalStatus.PENDING,
                    assigned_at=datetime.now(timezone.utc),
                )

                self.approval_task_repository.add(
                    next_approval_task
                )

            else:

                workflow_instance.status = (
                    WorkflowStatus.COMPLETED
                )

                workflow_instance.completed_at = (
                    datetime.now(timezone.utc)
                )

            # ONE COMMIT for the entire state transition
            self.db.commit()

            self.db.refresh(
                approval_task
            )

            return approval_task

        except Exception:

            self.db.rollback()

            raise


    def reject_task(
        self,
        approval_task_id: str,
        payload: ApprovalAction,
    ):
        try:
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

            if not payload.comments or not payload.comments.strip():
                raise ValueError(
                    "Rejection comments are required."
                )

            # Reject task
            approval_task.status = ApprovalStatus.REJECTED
            approval_task.comments = payload.comments.strip()
            approval_task.completed_at = datetime.now(
                timezone.utc
            )

            # Find parent workflow
            workflow_instance = (
                self.workflow_instance_repository.get_by_id(
                    approval_task.workflow_instance_id
                )
            )

            if workflow_instance is None:
                raise ValueError(
                    "Workflow Instance does not exist."
                )

            # Reject entire workflow
            workflow_instance.status = WorkflowStatus.REJECTED
            workflow_instance.completed_at = datetime.now(
                timezone.utc
            )

            # ONE COMMIT
            self.db.commit()

            self.db.refresh(
                approval_task
            )

            return approval_task

        except Exception:
            self.db.rollback()
            raise

            