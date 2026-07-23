from datetime import datetime, timezone

from sqlalchemy.orm import Session

from app.models.enums import (
    ApprovalStatus,
    AuditEventType,
    WorkflowStatus,
)
from app.models.workflow_instance import WorkflowInstance
from app.models.approval_task import ApprovalTask

from app.repositories.user_repository import (
    UserRepository,
)
from app.repositories.workflow_definition_repository import (
    WorkflowDefinitionRepository,
)
from app.repositories.workflow_step_repository import (
    WorkflowStepRepository,
)
from app.repositories.workflow_instance_repository import (
    WorkflowInstanceRepository,
)
from app.repositories.approval_task_repository import (
    ApprovalTaskRepository,
)

from app.schemas.workflow_instance import (
    WorkflowInstanceCreate,
)

from app.services.workflow_audit_service import (
    WorkflowAuditService,
)


class WorkflowInstanceService:

    def __init__(
        self,
        db: Session,
        user_repository: UserRepository,
        workflow_definition_repository: WorkflowDefinitionRepository,
        workflow_step_repository: WorkflowStepRepository,
        workflow_instance_repository: WorkflowInstanceRepository,
        approval_task_repository: ApprovalTaskRepository,
    ):
        # Keep the database session at service level.
        # The service owns the transaction boundary.
        self.db = db

        self.user_repository = (
            user_repository
        )

        self.workflow_definition_repository = (
            workflow_definition_repository
        )

        self.workflow_step_repository = (
            workflow_step_repository
        )

        self.workflow_instance_repository = (
            workflow_instance_repository
        )

        self.approval_task_repository = (
            approval_task_repository
        )

        self.audit_service = (
            WorkflowAuditService(db)
        )

    def start_workflow(
        self,
        payload: WorkflowInstanceCreate,
    ) -> WorkflowInstance:

        # =====================================================
        # STEP 1 — VALIDATE INITIATING USER
        # =====================================================

        user = self.user_repository.get_by_id(
            payload.initiated_by
        )

        if not user:
            raise ValueError(
                "Initiating user does not exist."
            )


        # =====================================================
        # STEP 2 — VALIDATE WORKFLOW DEFINITION
        # =====================================================

        workflow_definition = (
            self.workflow_definition_repository
            .get_by_id(
                payload.workflow_definition_id
            )
        )

        if not workflow_definition:
            raise ValueError(
                "Workflow Definition does not exist."
            )


        # =====================================================
        # STEP 3 — VALIDATE WORKFLOW IS ACTIVE
        # =====================================================

        if not workflow_definition.is_active:
            raise ValueError(
                "Workflow Definition is inactive."
            )


        # =====================================================
        # STEP 4 — GET AND VALIDATE WORKFLOW STEPS
        # =====================================================

        workflow_steps = (
            self.workflow_step_repository
            .get_by_workflow_definition(
                payload.workflow_definition_id
            )
        )

        if len(workflow_steps) == 0:
            raise ValueError(
                "Workflow contains no steps."
            )

        first_step = workflow_steps[0]


        # =====================================================
        # STEP 5 — BEGIN TRANSACTIONAL WORKFLOW CREATION
        # =====================================================

        try:

            # -------------------------------------------------
            # CREATE WORKFLOW INSTANCE
            # -------------------------------------------------

            workflow_instance = WorkflowInstance(
                workflow_definition_id=(
                    payload.workflow_definition_id
                ),
                initiated_by=(
                    payload.initiated_by
                ),
                status=(
                    WorkflowStatus.IN_PROGRESS
                ),
                current_step_order=1,
                started_at=(
                    datetime.now(timezone.utc)
                ),
            )

            # IMPORTANT:
            # add() must NOT commit.
            self.workflow_instance_repository.add(
                workflow_instance
            )

            # Flush so the instance is persisted inside
            # the current transaction and its ID is available.
            self.db.flush()


            # =================================================
            # STEP 6 — AUDIT: WORKFLOW_STARTED
            # =================================================

            self.audit_service.record_event(
                workflow_instance_id=(
                    workflow_instance.id
                ),
                event_type=(
                    AuditEventType.WORKFLOW_STARTED
                ),
                actor_id=(
                    payload.initiated_by
                ),
                from_status=None,
                to_status=(
                    workflow_instance.status.value
                ),
                event_metadata={
                    "workflow_definition_id": (
                        payload.workflow_definition_id
                    ),
                },
            )


            # =================================================
            # STEP 7 — CREATE INITIAL APPROVAL TASK
            # =================================================

            approval_task = ApprovalTask(
                workflow_instance_id=(
                    workflow_instance.id
                ),
                workflow_step_id=(
                    first_step.id
                ),

                # Temporary assignment strategy for V1.
                assigned_to=(
                    payload.initiated_by
                ),

                status=(
                    ApprovalStatus.PENDING
                ),

                assigned_at=(
                    datetime.now(timezone.utc)
                ),
            )

            # IMPORTANT:
            # add() must NOT commit.
            self.approval_task_repository.add(
                approval_task
            )

            # Flush so approval_task.id is available
            # for the audit-log foreign key.
            self.db.flush()


            # =================================================
            # STEP 8 — AUDIT: TASK_CREATED
            # =================================================

            self.audit_service.record_event(
                workflow_instance_id=(
                    workflow_instance.id
                ),
                approval_task_id=(
                    approval_task.id
                ),
                event_type=(
                    AuditEventType.TASK_CREATED
                ),
                actor_id=None,
                from_status=None,
                to_status=(
                    approval_task.status.value
                ),
                event_metadata={
                    "workflow_step_id": (
                        approval_task.workflow_step_id
                    ),
                    "step_order": (
                        first_step.step_order
                    ),
                },
            )


            # =================================================
            # STEP 9 — SINGLE TRANSACTION COMMIT
            # =================================================

            self.db.commit()

            self.db.refresh(
                workflow_instance
            )

            return workflow_instance


        except Exception:

            # Any failure in:
            #
            # - WorkflowInstance creation
            # - WORKFLOW_STARTED audit
            # - ApprovalTask creation
            # - TASK_CREATED audit
            #
            # rolls back the entire operation.

            self.db.rollback()

            raise