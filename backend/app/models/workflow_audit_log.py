from sqlalchemy import ForeignKey
from sqlalchemy import String
from sqlalchemy import JSON
from sqlalchemy import Enum as SqlEnum
from sqlalchemy.orm import Mapped
from sqlalchemy.orm import mapped_column
from sqlalchemy.orm import relationship

from app.models.base_entity import BaseEntity
from app.models.enums import AuditEventType


class WorkflowAuditLog(BaseEntity):
    __tablename__ = "workflow_audit_logs"

    workflow_instance_id: Mapped[str] = mapped_column(
        ForeignKey(
            "workflow_instances.id",
            ondelete="CASCADE",
        ),
        nullable=False,
        index=True,
    )

    approval_task_id: Mapped[str | None] = mapped_column(
        ForeignKey(
            "approval_tasks.id",
            ondelete="SET NULL",
        ),
        nullable=True,
    )

    actor_id: Mapped[str | None] = mapped_column(
        ForeignKey(
            "users.id",
            ondelete="SET NULL",
        ),
        nullable=True,
    )

    event_type: Mapped[AuditEventType] = mapped_column(
        SqlEnum(AuditEventType),
        nullable=False,
        index=True,
    )

    from_status: Mapped[str | None] = mapped_column(
        String(50),
        nullable=True,
    )

    to_status: Mapped[str | None] = mapped_column(
        String(50),
        nullable=True,
    )

    event_metadata: Mapped[dict | None] = mapped_column(
        JSON,
        nullable=True,
    )

    workflow_instance: Mapped["WorkflowInstance"] = relationship(
        back_populates="audit_logs",
    )