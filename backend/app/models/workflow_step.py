from sqlalchemy import Boolean
from sqlalchemy import ForeignKey
from sqlalchemy import Integer
from sqlalchemy import String
from sqlalchemy.orm import Mapped
from sqlalchemy.orm import mapped_column
from sqlalchemy.orm import relationship

from app.models.base_entity import BaseEntity


class WorkflowStep(BaseEntity):
    __tablename__ = "workflow_steps"

    workflow_definition_id: Mapped[str] = mapped_column(
        ForeignKey(
            "workflow_definitions.id",
            ondelete="CASCADE"
        ),
        nullable=False
    )

    workflow_definition: Mapped["WorkflowDefinition"] = relationship(
        "WorkflowDefinition",
        back_populates="steps",
    )

    step_order: Mapped[int] = mapped_column(
        Integer,
        nullable=False
    )

    step_name: Mapped[str] = mapped_column(
        String(255),
        nullable=False
    )

    approver_role: Mapped[str] = mapped_column(
        String(100),
        nullable=False
    )

    is_required: Mapped[bool] = mapped_column(
        Boolean,
        nullable=False,
        default=True
    )