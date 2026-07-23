from datetime import datetime
from typing import Any

from pydantic import BaseModel, ConfigDict

from app.models.enums import AuditEventType


class WorkflowAuditLogResponse(BaseModel):

    id: str

    workflow_instance_id: str

    approval_task_id: str | None

    actor_id: str | None

    event_type: AuditEventType

    from_status: str | None

    to_status: str | None

    event_metadata: dict[str, Any] | None

    created_at: datetime

    model_config = ConfigDict(
        from_attributes=True
    )