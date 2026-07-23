from datetime import datetime

from sqlalchemy import DateTime
from sqlalchemy import ForeignKey
from sqlalchemy import Integer
from sqlalchemy import Enum as SqlEnum
from sqlalchemy.orm import Mapped
from sqlalchemy.orm import mapped_column
from sqlalchemy.orm import relationship

from app.models.base_entity import BaseEntity
from app.models.enums import WorkflowStatus
from app.models.approval_task import ApprovalTask

class WorkflowInstance(BaseEntity):
    __tablename__ = "workflow_instances"

    workflow_definition_id: Mapped[str] = mapped_column(
        ForeignKey(
            "workflow_definitions.id",
            ondelete="CASCADE"
        ),
        nullable=False
    )

    initiated_by: Mapped[str] = mapped_column(
        ForeignKey(
            "users.id",
            ondelete="RESTRICT"
        ),
        nullable=False
    )

    status: Mapped[WorkflowStatus] = mapped_column(
        SqlEnum(WorkflowStatus),
        nullable=False,
        default=WorkflowStatus.PENDING
    )

    current_step_order: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        default=1
    )

    started_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False
    )

    completed_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True
    )

    workflow_definition: Mapped["WorkflowDefinition"] = relationship(
        back_populates="instances"
    )

    initiator: Mapped["User"] = relationship(
        back_populates="workflow_instances"
    )

    approval_tasks: Mapped[list["ApprovalTask"]] = relationship(
    "ApprovalTask",
    back_populates="workflow_instance",
    cascade="all, delete-orphan",
    )

    audit_logs: Mapped[list["WorkflowAuditLog"]] = relationship(
    back_populates="workflow_instance",
    cascade="all, delete-orphan",
    order_by="WorkflowAuditLog.created_at",
    )