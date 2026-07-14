from datetime import datetime

from pydantic import BaseModel


class WorkflowStepCreate(BaseModel):
    workflow_definition_id: str
    step_order: int
    step_name: str
    approver_role: str
    is_required: bool = True


class WorkflowStepResponse(BaseModel):
    id: str
    workflow_definition_id: str
    step_order: int
    step_name: str
    approver_role: str
    is_required: bool

    created_at: datetime
    updated_at: datetime

    model_config = {
        "from_attributes": True
    }