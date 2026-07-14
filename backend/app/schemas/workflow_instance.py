from datetime import datetime

from pydantic import BaseModel

from app.models.enums import WorkflowStatus


class WorkflowInstanceCreate(BaseModel):
    """
    Request schema for starting a workflow.
    """

    workflow_definition_id: str
    initiated_by: str


class WorkflowInstanceResponse(BaseModel):
    """
    Response schema returned after a workflow is created.
    """

    id: str
    workflow_definition_id: str
    initiated_by: str
    status: WorkflowStatus
    current_step_order: int
    started_at: datetime
    completed_at: datetime | None
    created_at: datetime
    updated_at: datetime

    model_config = {
        "from_attributes": True
    }