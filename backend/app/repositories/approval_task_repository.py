from sqlalchemy.orm import Session

from app.models.approval_task import ApprovalTask
from app.models.enums import ApprovalStatus


class ApprovalTaskRepository:
    """
    Handles database operations for Approval Tasks.
    """

    def __init__(
        self,
        db: Session,
    ):
        self.db = db

    def create(
        self,
        approval_task: ApprovalTask,
    ) -> ApprovalTask:

        self.db.add(approval_task)

        self.db.commit()

        self.db.refresh(approval_task)

        return approval_task

    def get_by_id(
        self,
        approval_task_id: str,
    ) -> ApprovalTask | None:

        return (
            self.db.query(ApprovalTask)
            .filter(
                ApprovalTask.id == approval_task_id
            )
            .first()
        )

    def get_pending_tasks_for_user(
        self,
        user_id: str,
    ) -> list[ApprovalTask]:

        return (
            self.db.query(ApprovalTask)
            .filter(
                ApprovalTask.assigned_to == user_id,
                ApprovalTask.status == ApprovalStatus.PENDING,
            )
            .all()
        )

    def update(
        self,
        approval_task: ApprovalTask,
    ) -> ApprovalTask:

        self.db.commit()

        self.db.refresh(approval_task)

        return approval_task