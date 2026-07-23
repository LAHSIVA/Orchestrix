from datetime import datetime, timezone

from sqlalchemy.orm import Session

from app.models.enums import (
    ApprovalStatus,
    WorkflowStatus,
    AuditEventType,
)
from app.models.approval_task import ApprovalTask

from app.schemas.approval_task import ApprovalAction

from app.repositories.approval_task_repository import (
    ApprovalTaskRepository,
)
from app.repositories.workflow_instance_repository import (
    WorkflowInstanceRepository,
)
from app.repositories.workflow_step_repository import (
    WorkflowStepRepository,
)

from app.services.workflow_audit_service import (
    WorkflowAuditService,
)


class ApprovalTaskService:

    def __init__(
        self,
        db: Session,
        approval_task_repository: ApprovalTaskRepository,
        workflow_instance_repository: WorkflowInstanceRepository,
        workflow_step_repository: WorkflowStepRepository,
    ):
        # -----------------------------------------------------
        # Shared database session
        # -----------------------------------------------------
        #
        # All workflow state changes and audit events use
        # this same session so they participate in one
        # database transaction.
        # -----------------------------------------------------

        self.db = db

        self.approval_task_repository = (
            approval_task_repository
        )

        self.workflow_instance_repository = (
            workflow_instance_repository
        )

        self.workflow_step_repository = (
            workflow_step_repository
        )

        self.audit_service = WorkflowAuditService(
            db
        )


    # =========================================================
    # APPROVE TASK
    # =========================================================

    def approve_task(
        self,
        approval_task_id: str,
        payload: ApprovalAction,
    ):
        try:

            # =================================================
            # STEP 1 — FIND APPROVAL TASK
            # =================================================

            approval_task = (
                self.approval_task_repository.get_by_id(
                    approval_task_id
                )
            )

            if approval_task is None:
                raise ValueError(
                    "Approval Task does not exist."
                )


            # =================================================
            # STEP 2 — PREVENT DUPLICATE PROCESSING
            # =================================================

            if (
                approval_task.status
                != ApprovalStatus.PENDING
            ):
                raise ValueError(
                    "Approval Task has already been processed."
                )


            # =================================================
            # STEP 3 — SAVE PREVIOUS TASK STATUS
            # =================================================
            #
            # We capture this BEFORE changing the status so
            # the audit log can record:
            #
            # PENDING -> APPROVED
            # =================================================

            previous_task_status = (
                approval_task.status.value
            )


            # =================================================
            # STEP 4 — APPROVE CURRENT TASK
            # =================================================

            approval_task.status = (
                ApprovalStatus.APPROVED
            )

            approval_task.comments = (
                payload.comments
            )

            approval_task.completed_at = (
                datetime.now(timezone.utc)
            )


            # =================================================
            # STEP 5 — FIND PARENT WORKFLOW INSTANCE
            # =================================================

            workflow_instance = (
                self.workflow_instance_repository.get_by_id(
                    approval_task.workflow_instance_id
                )
            )

            if workflow_instance is None:
                raise ValueError(
                    "Workflow Instance does not exist."
                )


            # =================================================
            # STEP 6 — AUDIT: TASK_APPROVED
            # =================================================

            self.audit_service.record_event(
                workflow_instance_id=(
                    workflow_instance.id
                ),
                approval_task_id=(
                    approval_task.id
                ),
                event_type=(
                    AuditEventType.TASK_APPROVED
                ),
                actor_id=(
                    approval_task.assigned_to
                ),
                from_status=(
                    previous_task_status
                ),
                to_status=(
                    approval_task.status.value
                ),
                event_metadata={
                    "comments": (
                        approval_task.comments
                    ),
                    "workflow_step_id": (
                        approval_task.workflow_step_id
                    ),
                },
            )


            # =================================================
            # STEP 7 — FIND NEXT WORKFLOW STEP
            # =================================================

            previous_step_order = (
                workflow_instance.current_step_order
            )

            next_step = (
                self.workflow_step_repository.get_next_step(
                    workflow_definition_id=(
                        workflow_instance
                        .workflow_definition_id
                    ),
                    current_step_order=(
                        workflow_instance
                        .current_step_order
                    ),
                )
            )


            # =================================================
            # STEP 8A — NEXT STEP EXISTS
            # =================================================

            if next_step is not None:

                # ---------------------------------------------
                # Advance workflow
                # ---------------------------------------------

                workflow_instance.current_step_order = (
                    next_step.step_order
                )


                # ---------------------------------------------
                # AUDIT: WORKFLOW_ADVANCED
                # ---------------------------------------------

                self.audit_service.record_event(
                    workflow_instance_id=(
                        workflow_instance.id
                    ),
                    event_type=(
                        AuditEventType.WORKFLOW_ADVANCED
                    ),
                    actor_id=(
                        approval_task.assigned_to
                    ),
                    from_status=None,
                    to_status=None,
                    event_metadata={
                        "from_step_order": (
                            previous_step_order
                        ),
                        "to_step_order": (
                            workflow_instance
                            .current_step_order
                        ),
                    },
                )


                # ---------------------------------------------
                # Create next approval task
                # ---------------------------------------------

                next_approval_task = ApprovalTask(
                    workflow_instance_id=(
                        workflow_instance.id
                    ),
                    workflow_step_id=(
                        next_step.id
                    ),

                    # Temporary V1 assignment strategy.
                    assigned_to=(
                        workflow_instance.initiated_by
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
                #
                # This keeps next-task creation inside the
                # same transaction as task approval,
                # workflow advancement and audit events.

                self.approval_task_repository.add(
                    next_approval_task
                )


                # ---------------------------------------------
                # Flush to obtain/guarantee task ID
                # ---------------------------------------------

                self.db.flush()


                # ---------------------------------------------
                # AUDIT: TASK_CREATED
                # ---------------------------------------------

                self.audit_service.record_event(
                    workflow_instance_id=(
                        workflow_instance.id
                    ),
                    approval_task_id=(
                        next_approval_task.id
                    ),
                    event_type=(
                        AuditEventType.TASK_CREATED
                    ),
                    actor_id=None,
                    from_status=None,
                    to_status=(
                        next_approval_task.status.value
                    ),
                    event_metadata={
                        "workflow_step_id": (
                            next_approval_task
                            .workflow_step_id
                        ),
                    },
                )


            # =================================================
            # STEP 8B — NO NEXT STEP
            # =================================================
            #
            # This means the final approval task has been
            # approved and the workflow is complete.
            # =================================================

            else:

                previous_workflow_status = (
                    workflow_instance.status.value
                )


                # ---------------------------------------------
                # Complete workflow
                # ---------------------------------------------

                workflow_instance.status = (
                    WorkflowStatus.COMPLETED
                )

                workflow_instance.completed_at = (
                    datetime.now(timezone.utc)
                )


                # ---------------------------------------------
                # AUDIT: WORKFLOW_COMPLETED
                # ---------------------------------------------

                self.audit_service.record_event(
                    workflow_instance_id=(
                        workflow_instance.id
                    ),
                    event_type=(
                        AuditEventType.WORKFLOW_COMPLETED
                    ),
                    actor_id=(
                        approval_task.assigned_to
                    ),
                    from_status=(
                        previous_workflow_status
                    ),
                    to_status=(
                        workflow_instance.status.value
                    ),
                    event_metadata={
                        "final_approval_task_id": (
                            approval_task.id
                        ),
                    },
                )


            # =================================================
            # STEP 9 — ONE ATOMIC COMMIT
            # =================================================
            #
            # Intermediate approval:
            #
            #   Task APPROVED
            #   TASK_APPROVED audit
            #   Workflow advanced
            #   WORKFLOW_ADVANCED audit
            #   Next task created
            #   TASK_CREATED audit
            #
            # Final approval:
            #
            #   Task APPROVED
            #   TASK_APPROVED audit
            #   Workflow COMPLETED
            #   WORKFLOW_COMPLETED audit
            #
            # Everything commits together.
            # =================================================

            self.db.commit()


            # =================================================
            # STEP 10 — REFRESH RESULT
            # =================================================

            self.db.refresh(
                approval_task
            )

            return approval_task


        except Exception:

            # =================================================
            # ATOMIC ROLLBACK
            # =================================================
            #
            # Any failure rolls back BOTH:
            #
            # - business state changes
            # - audit-log changes
            #
            # No partial history should survive.
            # =================================================

            self.db.rollback()

            raise


    # =========================================================
    # REJECT TASK
    # =========================================================

    def reject_task(
        self,
        approval_task_id: str,
        payload: ApprovalAction,
    ):
        try:

            # =================================================
            # STEP 1 — FIND APPROVAL TASK
            # =================================================

            approval_task = (
                self.approval_task_repository.get_by_id(
                    approval_task_id
                )
            )

            if approval_task is None:
                raise ValueError(
                    "Approval Task does not exist."
                )


            # =================================================
            # STEP 2 — PREVENT DUPLICATE PROCESSING
            # =================================================

            if (
                approval_task.status
                != ApprovalStatus.PENDING
            ):
                raise ValueError(
                    "Approval Task has already been processed."
                )


            # =================================================
            # STEP 3 — REQUIRE REJECTION COMMENTS
            # =================================================

            if (
                not payload.comments
                or not payload.comments.strip()
            ):
                raise ValueError(
                    "Rejection comments are required."
                )


            # =================================================
            # STEP 4 — SAVE PREVIOUS TASK STATUS
            # =================================================

            previous_task_status = (
                approval_task.status.value
            )


            # =================================================
            # STEP 5 — REJECT TASK
            # =================================================

            approval_task.status = (
                ApprovalStatus.REJECTED
            )

            approval_task.comments = (
                payload.comments.strip()
            )

            approval_task.completed_at = (
                datetime.now(timezone.utc)
            )


            # =================================================
            # STEP 6 — FIND PARENT WORKFLOW
            # =================================================

            workflow_instance = (
                self.workflow_instance_repository.get_by_id(
                    approval_task.workflow_instance_id
                )
            )

            if workflow_instance is None:
                raise ValueError(
                    "Workflow Instance does not exist."
                )


            # =================================================
            # STEP 7 — SAVE PREVIOUS WORKFLOW STATUS
            # =================================================

            previous_workflow_status = (
                workflow_instance.status.value
            )


            # =================================================
            # STEP 8 — AUDIT: TASK_REJECTED
            # =================================================

            self.audit_service.record_event(
                workflow_instance_id=(
                    workflow_instance.id
                ),
                approval_task_id=(
                    approval_task.id
                ),
                event_type=(
                    AuditEventType.TASK_REJECTED
                ),
                actor_id=(
                    approval_task.assigned_to
                ),
                from_status=(
                    previous_task_status
                ),
                to_status=(
                    approval_task.status.value
                ),
                event_metadata={
                    "comments": (
                        approval_task.comments
                    ),
                    "workflow_step_id": (
                        approval_task.workflow_step_id
                    ),
                },
            )


            # =================================================
            # STEP 9 — REJECT ENTIRE WORKFLOW
            # =================================================

            workflow_instance.status = (
                WorkflowStatus.REJECTED
            )

            workflow_instance.completed_at = (
                datetime.now(timezone.utc)
            )


            # =================================================
            # STEP 10 — AUDIT: WORKFLOW_REJECTED
            # =================================================

            self.audit_service.record_event(
                workflow_instance_id=(
                    workflow_instance.id
                ),
                event_type=(
                    AuditEventType.WORKFLOW_REJECTED
                ),
                actor_id=(
                    approval_task.assigned_to
                ),
                from_status=(
                    previous_workflow_status
                ),
                to_status=(
                    workflow_instance.status.value
                ),
                event_metadata={
                    "rejected_approval_task_id": (
                        approval_task.id
                    ),
                },
            )


            # =================================================
            # STEP 11 — ONE ATOMIC COMMIT
            # =================================================

            self.db.commit()


            # =================================================
            # STEP 12 — REFRESH RESULT
            # =================================================

            self.db.refresh(
                approval_task
            )

            return approval_task


        except Exception:

            self.db.rollback()

            raise