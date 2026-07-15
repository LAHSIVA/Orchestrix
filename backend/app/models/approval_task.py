from datetime import datetime

from sqlalchemy import DateTime
from sqlalchemy import ForeignKey
from sqlalchemy import String
from sqlalchemy import Text
from sqlalchemy import Enum as SqlEnum
from sqlalchemy.orm import Mapped
from sqlalchemy.orm import mapped_column
from sqlalchemy.orm import relationship

from app.models.base_entity import BaseEntity
from app.models.enums import ApprovalStatus


class ApprovalTask(BaseEntity):
    __tablename__ = "approval_tasks"

    workflow_instance_id: Mapped[str] = mapped_column(
        ForeignKey(
            "workflow_instances.id",
            ondelete="CASCADE",
        ),
        nullable=False,
    )

    workflow_step_id: Mapped[str] = mapped_column(
        ForeignKey(
            "workflow_steps.id",
            ondelete="CASCADE",
        ),
        nullable=False,
    )

    assigned_to: Mapped[str] = mapped_column(
        ForeignKey(
            "users.id",
            ondelete="RESTRICT",
        ),
        nullable=False,
    )

    status: Mapped[ApprovalStatus] = mapped_column(
        SqlEnum(ApprovalStatus),
        nullable=False,
        default=ApprovalStatus.PENDING,
    )

    comments: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
    )

    assigned_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
    )

    completed_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
    )

    workflow_instance: Mapped["WorkflowInstance"] = relationship(
        "WorkflowInstance",
        back_populates="approval_tasks",
    )

    workflow_step: Mapped["WorkflowStep"] = relationship(
        "WorkflowStep",
        back_populates="approval_tasks",
    )

    assignee: Mapped["User"] = relationship(
        "User",
        back_populates="approval_tasks",
    )