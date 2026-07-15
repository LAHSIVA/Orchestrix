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


    def get_by_id(
        self,
        workflow_instance_id: str,
    ) -> WorkflowInstance | None:

        return (
            self.db.query(WorkflowInstance)
            .filter(
                WorkflowInstance.id == workflow_instance_id
            )
            .first()
        )
    
    def get_all(self) -> list[WorkflowInstance]:

        return (
            self.db.query(WorkflowInstance)
            .order_by(
                WorkflowInstance.created_at.desc()
            )
            .all()
        )

    def update(
        self,
        workflow_instance: WorkflowInstance,
    ) -> WorkflowInstance:

            self.db.commit()

            self.db.refresh(workflow_instance)

            return workflow_instance