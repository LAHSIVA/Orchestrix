from app.models.workflow_definition import WorkflowDefinition
from app.repositories.workflow_definition_repository import (
    WorkflowDefinitionRepository,
)
from app.schemas.workflow_definition import (
    WorkflowDefinitionCreate,
)


class WorkflowDefinitionService:
    """
    Business logic for workflow definitions.
    """

    def __init__(
        self,
        repository: WorkflowDefinitionRepository,
    ):
        self.repository = repository

    def create_workflow_definition(
        self,
        payload: WorkflowDefinitionCreate,
    ) -> WorkflowDefinition:

        existing = self.repository.get_by_name(payload.name)

        if existing:
            raise ValueError(
                "Workflow definition with this name already exists."
            )

        workflow_definition = WorkflowDefinition(
            name=payload.name,
            description=payload.description,
            version=1,
            is_active=True,
        )

        return self.repository.create(workflow_definition)

    def get_workflow_definitions(
        self,
    ) -> list[WorkflowDefinition]:

        return self.repository.get_all()