from sqlalchemy.orm import Session

from app.models.workflow_step import WorkflowStep


class WorkflowStepRepository:
    """
    Handles database operations for Workflow Steps.
    """

    def __init__(self, db: Session):
        self.db = db

    def create(
        self,
        workflow_step: WorkflowStep,
    ) -> WorkflowStep:

        self.db.add(workflow_step)

        self.db.commit()

        self.db.refresh(workflow_step)

        return workflow_step

    def get_by_workflow_definition(
        self,
        workflow_definition_id: str,
    ) -> list[WorkflowStep]:

        return (
            self.db.query(WorkflowStep)
            .filter(
                WorkflowStep.workflow_definition_id
                == workflow_definition_id
            )
            .order_by(WorkflowStep.step_order)
            .all()
        )

    def get_by_definition_and_order(
        self,
        workflow_definition_id: str,
        step_order: int,
    ) -> WorkflowStep | None:

        return (
            self.db.query(WorkflowStep)
            .filter(
                WorkflowStep.workflow_definition_id
                == workflow_definition_id,
                WorkflowStep.step_order
                == step_order,
            )
            .first()
        )
    
    def get_next_step(
        self,
        workflow_definition_id: str,
        current_step_order: int,
    ) -> WorkflowStep | None:

        return (
            self.db.query(WorkflowStep)
            .filter(
                WorkflowStep.workflow_definition_id
                == workflow_definition_id,
                WorkflowStep.step_order
                == current_step_order + 1,
            )
            .first()
        )