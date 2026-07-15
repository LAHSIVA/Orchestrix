from sqlalchemy import Enum
from sqlalchemy import String
from sqlalchemy.orm import Mapped
from sqlalchemy.orm import mapped_column

from app.models.base_entity import BaseEntity
from app.models.enums import UserRole
from app.models.enums import UserStatus
from sqlalchemy.orm import relationship

from app.models.approval_task import ApprovalTask



class User(BaseEntity):
    __tablename__ = "users"

    name: Mapped[str] = mapped_column(
        String(255),
        nullable=False
    )

    email: Mapped[str] = mapped_column(
        String(255),
        unique=True,
        nullable=False,
        index=True
    )

    role: Mapped[UserRole] = mapped_column(
        Enum(UserRole),
        nullable=False
    )

    status: Mapped[UserStatus] = mapped_column(
        Enum(UserStatus),
        nullable=False,
        default=UserStatus.ACTIVE
    )

    workflow_instances: Mapped[list["WorkflowInstance"]] = relationship(
    back_populates="initiator"
    )

    approval_tasks: Mapped[list["ApprovalTask"]] = relationship(
    "ApprovalTask",
    back_populates="assignee",
    )