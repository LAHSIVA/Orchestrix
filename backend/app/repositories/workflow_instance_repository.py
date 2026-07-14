from sqlalchemy.orm import Session

from app.models.workflow_instance import WorkflowInstance


class WorkflowInstanceRepository:
    """
    Handles database operations for WorkflowInstance.
    """

    def __init__(self, db: Session):
        self.db = db

    def create(
        self,
        workflow_instance: WorkflowInstance
    ) -> WorkflowInstance:

        self.db.add(workflow_instance)

        self.db.commit()

        self.db.refresh(workflow_instance)

        return workflow_instance