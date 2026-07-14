from sqlalchemy.orm import Session

from app.models.workflow_definition import WorkflowDefinition


class WorkflowDefinitionRepository:
    """
    Handles database operations for Workflow Definitions.
    """

    def __init__(self, db: Session):
        self.db = db

    def create(
        self,
        workflow_definition: WorkflowDefinition,
    ) -> WorkflowDefinition:

        self.db.add(workflow_definition)

        self.db.commit()

        self.db.refresh(workflow_definition)

        return workflow_definition

    def get_by_name(
        self,
        name: str,
    ) -> WorkflowDefinition | None:

        return (
            self.db.query(WorkflowDefinition)
            .filter(
                WorkflowDefinition.name == name
            )
            .first()
        )

    def get_all(self) -> list[WorkflowDefinition]:

        return (
            self.db.query(WorkflowDefinition)
            .order_by(WorkflowDefinition.created_at.desc())
            .all()
        )

    def get_by_id(
        self,
        workflow_definition_id: str,
    ) -> WorkflowDefinition | None:

        return (
            self.db.query(WorkflowDefinition)
            .filter(
                WorkflowDefinition.id == workflow_definition_id
            )
            .first()
        )