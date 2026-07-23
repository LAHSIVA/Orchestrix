from sqlalchemy.orm import Session

from app.models.workflow_audit_log import WorkflowAuditLog


class WorkflowAuditLogRepository:
    """
    Handles database operations for workflow audit logs.

    Important:
    This repository does NOT commit transactions.

    Transaction ownership belongs to the service layer
    so workflow state changes and audit events remain atomic.
    """

    def __init__(
        self,
        db: Session,
    ):
        self.db = db

    def add(
        self,
        audit_log: WorkflowAuditLog,
    ) -> WorkflowAuditLog:

        self.db.add(audit_log)

        return audit_log

    def get_by_workflow_instance_id(
        self,
        workflow_instance_id: str,
    ) -> list[WorkflowAuditLog]:

        return (
            self.db.query(WorkflowAuditLog)
            .filter(
                WorkflowAuditLog.workflow_instance_id
                == workflow_instance_id
            )
            .order_by(
                WorkflowAuditLog.created_at.asc()
            )
            .all()
        )