from datetime import datetime

from pydantic import BaseModel


class WorkflowDefinitionCreate(BaseModel):
    """
    Request schema for creating a workflow definition.
    """

    name: str
    description: str


class WorkflowDefinitionResponse(BaseModel):
    """
    Response schema for workflow definition.
    """

    id: str
    name: str
    description: str
    version: int
    is_active: bool
    created_at: datetime
    updated_at: datetime

    model_config = {
        "from_attributes": True
    }