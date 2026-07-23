from sqlalchemy.orm import Session

from app.models.enums import AuditEventType
from app.models.workflow_audit_log import WorkflowAuditLog
from app.repositories.workflow_audit_log_repository import (
    WorkflowAuditLogRepository,
)


class WorkflowAuditService:

    def __init__(
        self,
        db: Session,
    ):
        self.db = db

        self.repository = (
            WorkflowAuditLogRepository(db)
        )

    def record_event(
        self,
        *,
        workflow_instance_id: str,
        event_type: AuditEventType,
        approval_task_id: str | None = None,
        actor_id: str | None = None,
        from_status: str | None = None,
        to_status: str | None = None,
        event_metadata: dict | None = None,
    ) -> WorkflowAuditLog:

        audit_log = WorkflowAuditLog(
            workflow_instance_id=(
                workflow_instance_id
            ),
            approval_task_id=approval_task_id,
            actor_id=actor_id,
            event_type=event_type,
            from_status=from_status,
            to_status=to_status,
            event_metadata=event_metadata,
        )

        self.repository.add(
            audit_log
        )

        return audit_log

    def get_history(
    self,
    workflow_instance_id: str,
    ) -> list[WorkflowAuditLog]:

        return (
            self.repository
            .get_by_workflow_instance_id(
                workflow_instance_id
            )
        )