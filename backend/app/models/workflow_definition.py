import uuid

from sqlalchemy import Boolean
from sqlalchemy import Integer
from sqlalchemy import String
from sqlalchemy.orm import Mapped
from sqlalchemy.orm import mapped_column
from sqlalchemy.orm import relationship

from app.models.base_entity import BaseEntity

class WorkflowDefinition(BaseEntity):
    __tablename__ = "workflow_definitions"


    name: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
        unique=True
    )

    description: Mapped[str] = mapped_column(
        String(1000),
        nullable=False
    )

    version: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        default=1
    )

    is_active: Mapped[bool] = mapped_column(
        Boolean,
        nullable=False,
        default=True
    )

    steps: Mapped[list["WorkflowStep"]] = relationship(
        back_populates="workflow_definition",
        cascade="all, delete-orphan",
        order_by="WorkflowStep.step_order"
    )

    instances: Mapped[list["WorkflowInstance"]] = relationship(
    back_populates="workflow_definition",
    cascade="all, delete-orphan"
)