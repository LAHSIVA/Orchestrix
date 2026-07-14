from app.models.workflow_step import WorkflowStep
from app.repositories.workflow_step_repository import WorkflowStepRepository
from app.schemas.workflow_step import WorkflowStepCreate


class WorkflowStepService:

    def __init__(
        self,
        repository: WorkflowStepRepository,
    ):
        self.repository = repository

    def create_workflow_step(
        self,
        payload: WorkflowStepCreate,
    ) -> WorkflowStep:

        existing_step = (
            self.repository.get_by_definition_and_order(
                payload.workflow_definition_id,
                payload.step_order,
            )
        )

        if existing_step:
            raise ValueError(
                "A workflow step with this order already exists."
            )

        workflow_step = WorkflowStep(
            workflow_definition_id=payload.workflow_definition_id,
            step_order=payload.step_order,
            step_name=payload.step_name,
            approver_role=payload.approver_role,
            is_required=payload.is_required,
        )

        return self.repository.create(workflow_step)

    def get_workflow_steps(
        self,
        workflow_definition_id: str,
    ):

        return self.repository.get_by_workflow_definition(
            workflow_definition_id
        )