from sqlalchemy.orm import Session

from app.models.workflow_instance import WorkflowInstance


class WorkflowInstanceRepository:
    """
    Handles database operations for WorkflowInstance.

    Transaction design:

    - add():
        Adds an entity to the current SQLAlchemy transaction.
        Does NOT commit.

    - create():
        Convenience method for standalone creation.
        Commits immediately.

    - update():
        Convenience method for standalone updates.
        Commits immediately.

    For multi-table workflow operations, the service layer
    should use add() and control commit/rollback itself.
    """

    def __init__(
        self,
        db: Session,
    ):
        self.db = db


    # =========================================================
    # ADD — NO COMMIT
    # =========================================================

    def add(
        self,
        workflow_instance: WorkflowInstance,
    ) -> WorkflowInstance:
        """
        Add a WorkflowInstance to the current transaction.

        IMPORTANT:
        This method does NOT commit.

        Use this method when WorkflowInstance changes must be
        atomic with other operations such as:

        - ApprovalTask creation
        - Audit log creation
        - Workflow state transitions

        The service layer owns commit/rollback.
        """

        self.db.add(
            workflow_instance
        )

        return workflow_instance


    # =========================================================
    # CREATE — STANDALONE COMMIT
    # =========================================================

    def create(
        self,
        workflow_instance: WorkflowInstance,
    ) -> WorkflowInstance:
        """
        Create and immediately persist a WorkflowInstance.

        Prefer add() for multi-table transactional operations.
        """

        self.db.add(
            workflow_instance
        )

        self.db.commit()

        self.db.refresh(
            workflow_instance
        )

        return workflow_instance


    # =========================================================
    # GET BY ID
    # =========================================================

    def get_by_id(
        self,
        workflow_instance_id: str,
    ) -> WorkflowInstance | None:

        return (
            self.db.query(
                WorkflowInstance
            )
            .filter(
                WorkflowInstance.id
                == workflow_instance_id
            )
            .first()
        )


    # =========================================================
    # GET ALL
    # =========================================================

    def get_all(
        self,
    ) -> list[WorkflowInstance]:

        return (
            self.db.query(
                WorkflowInstance
            )
            .order_by(
                WorkflowInstance.created_at.desc()
            )
            .all()
        )


    # =========================================================
    # UPDATE — STANDALONE COMMIT
    # =========================================================

    def update(
        self,
        workflow_instance: WorkflowInstance,
    ) -> WorkflowInstance:
        """
        Persist changes and commit immediately.

        For atomic workflow-engine operations where multiple
        entities are changed together, avoid this method and
        let the service layer perform one final db.commit().
        """

        self.db.add(
            workflow_instance
        )

        self.db.commit()

        self.db.refresh(
            workflow_instance
        )

        return workflow_instance