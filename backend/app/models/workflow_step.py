import uuid
from datetime import datetime

from sqlalchemy import Boolean
from sqlalchemy import DateTime
from sqlalchemy import ForeignKey
from sqlalchemy import Integer
from sqlalchemy import String
from sqlalchemy import func
from sqlalchemy.orm import Mapped
from sqlalchemy.orm import mapped_column

from app.db.base import Base


class WorkflowStep(Base):
    __tablename__ = "workflow_steps"

    id: Mapped[str] = mapped_column(
        String,
        primary_key=True,
        default=lambda: str(uuid.uuid4())
    )

    workflow_definition_id: Mapped[str] = mapped_column(
        ForeignKey("workflow_definitions.id"),
        nullable=False
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
        default=True
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now()
    )

    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now()
    )