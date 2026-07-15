from datetime import datetime

from pydantic import BaseModel

from app.models.enums import ApprovalStatus


class ApprovalAction(BaseModel):
    comments: str | None = None


class ApprovalTaskResponse(BaseModel):
    id: str

    workflow_instance_id: str

    workflow_step_id: str

    assigned_to: str

    status: ApprovalStatus

    comments: str | None

    assigned_at: datetime

    completed_at: datetime | None

    created_at: datetime

    updated_at: datetime

    model_config = {
        "from_attributes": True
    }