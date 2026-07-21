from app.models.approval_task import ApprovalTask
from app.models.workflow_instance import WorkflowInstance
from unittest.mock import patch


def test_multi_step_workflow_completes_successfully(
    client,
    db_session,
):
    """
    End-to-end happy-path test.

    Flow:
        Create user
            ↓
        Create workflow definition
            ↓
        Create Step 1
            ↓
        Create Step 2
            ↓
        Start workflow instance
            ↓
        Verify Task #1 is PENDING
            ↓
        Approve Task #1
            ↓
        Verify workflow advances to Step 2
            ↓
        Verify Task #2 is created
            ↓
        Approve Task #2
            ↓
        Verify workflow becomes COMPLETED
    """

    # =========================================================
    # STEP 1 — CREATE USER
    # =========================================================

    user_response = client.post(
        "/users",
        json={
            "name": "Workflow Test EMPLOYEE",
            "email": "workflow.EMPLOYEE@test.com",
            "role": "EMPLOYEE",
        },
    )

    assert user_response.status_code in (200, 201), (
        f"User creation failed: "
        f"{user_response.status_code} "
        f"{user_response.text}"
    )

    user_data = user_response.json()

    user_id = user_data["id"]

    assert user_id is not None


    # =========================================================
    # STEP 2 — CREATE WORKFLOW DEFINITION
    # =========================================================

    workflow_response = client.post(
        "/workflow-definitions",
        json={
            "name": "Automated Expense Approval",
            "description": (
                "Two-step expense approval workflow "
                "created during automated testing."
            ),
        },
    )

    assert workflow_response.status_code in (200, 201), (
        f"Workflow definition creation failed: "
        f"{workflow_response.status_code} "
        f"{workflow_response.text}"
    )

    workflow_data = workflow_response.json()

    workflow_definition_id = workflow_data["id"]

    assert workflow_definition_id is not None


    # =========================================================
    # STEP 3 — CREATE WORKFLOW STEP #1
    # =========================================================

    step_1_response = client.post(
        "/workflow-steps",
        json={
            "workflow_definition_id": workflow_definition_id,
            "step_order": 1,
            "step_name": "EMPLOYEE Approval",
            "approver_role": "EMPLOYEE",
            "is_required": True,
        },
    )

    assert step_1_response.status_code in (200, 201), (
        f"Step 1 creation failed: "
        f"{step_1_response.status_code} "
        f"{step_1_response.text}"
    )

    step_1_data = step_1_response.json()

    step_1_id = step_1_data["id"]

    assert step_1_id is not None


    # =========================================================
    # STEP 4 — CREATE WORKFLOW STEP #2
    # =========================================================

    step_2_response = client.post(
        "/workflow-steps",
        json={
            "workflow_definition_id": workflow_definition_id,
            "step_order": 2,
            "step_name": "Finance Approval",
            "approver_role": "EMPLOYEE",
            "is_required": True,
        },
    )

    assert step_2_response.status_code in (200, 201), (
        f"Step 2 creation failed: "
        f"{step_2_response.status_code} "
        f"{step_2_response.text}"
    )

    step_2_data = step_2_response.json()

    step_2_id = step_2_data["id"]

    assert step_2_id is not None


    # =========================================================
    # STEP 5 — START WORKFLOW INSTANCE
    # =========================================================

    instance_response = client.post(
        "/workflow-instances",
        json={
            "workflow_definition_id": workflow_definition_id,
            "initiated_by": user_id,
        },
    )

    assert instance_response.status_code in (200, 201), (
        f"Workflow instance creation failed: "
        f"{instance_response.status_code} "
        f"{instance_response.text}"
    )

    instance_data = instance_response.json()

    workflow_instance_id = instance_data["id"]

    assert workflow_instance_id is not None


    # =========================================================
    # STEP 6 — VERIFY INITIAL WORKFLOW STATE
    # =========================================================

    db_session.expire_all()

    workflow_instance = (
        db_session.query(WorkflowInstance)
        .filter(
            WorkflowInstance.id == workflow_instance_id
        )
        .first()
    )

    assert workflow_instance is not None

    assert workflow_instance.current_step_order == 1

    assert workflow_instance.status.value in (
        "PENDING",
        "IN_PROGRESS",
    )


    # =========================================================
    # STEP 7 — FIND APPROVAL TASK #1
    # =========================================================

    task_1 = (
        db_session.query(ApprovalTask)
        .filter(
            ApprovalTask.workflow_instance_id
            == workflow_instance_id,
            ApprovalTask.workflow_step_id
            == step_1_id,
        )
        .first()
    )

    assert task_1 is not None, (
        "Approval Task #1 was not automatically created."
    )

    assert task_1.status.value == "PENDING"

    task_1_id = task_1.id


    # =========================================================
    # STEP 8 — APPROVE TASK #1
    # =========================================================

    approve_task_1_response = client.post(
        f"/approval-tasks/{task_1_id}/approve",
        json={
            "comments": (
                "EMPLOYEE approval completed "
                "during automated test."
            )
        },
    )

    assert approve_task_1_response.status_code in (
        200,
        201,
    ), (
        f"Task #1 approval failed: "
        f"{approve_task_1_response.status_code} "
        f"{approve_task_1_response.text}"
    )


    # =========================================================
    # STEP 9 — VERIFY TASK #1 BECAME APPROVED
    # =========================================================

    db_session.expire_all()

    task_1 = (
        db_session.query(ApprovalTask)
        .filter(
            ApprovalTask.id == task_1_id
        )
        .first()
    )

    assert task_1 is not None

    assert task_1.status.value == "APPROVED"

    assert task_1.completed_at is not None


    # =========================================================
    # STEP 10 — VERIFY WORKFLOW MOVED TO STEP #2
    # =========================================================

    db_session.expire_all()

    workflow_instance = (
        db_session.query(WorkflowInstance)
        .filter(
            WorkflowInstance.id == workflow_instance_id
        )
        .first()
    )

    assert workflow_instance is not None

    assert workflow_instance.current_step_order == 2

    assert workflow_instance.status.value in (
        "PENDING",
        "IN_PROGRESS",
    )


    # =========================================================
    # STEP 11 — VERIFY TASK #2 WAS CREATED
    # =========================================================

    task_2 = (
        db_session.query(ApprovalTask)
        .filter(
            ApprovalTask.workflow_instance_id
            == workflow_instance_id,
            ApprovalTask.workflow_step_id
            == step_2_id,
        )
        .first()
    )

    assert task_2 is not None, (
        "Approval Task #2 was not created "
        "after Task #1 approval."
    )

    assert task_2.status.value == "PENDING"

    task_2_id = task_2.id

    assert task_2_id != task_1_id


    # =========================================================
    # STEP 12 — APPROVE TASK #2
    # =========================================================

    approve_task_2_response = client.post(
        f"/approval-tasks/{task_2_id}/approve",
        json={
            "comments": (
                "Finance approval completed "
                "during automated test."
            )
        },
    )

    assert approve_task_2_response.status_code in (
        200,
        201,
    ), (
        f"Task #2 approval failed: "
        f"{approve_task_2_response.status_code} "
        f"{approve_task_2_response.text}"
    )


    # =========================================================
    # STEP 13 — VERIFY TASK #2 BECAME APPROVED
    # =========================================================

    db_session.expire_all()

    task_2 = (
        db_session.query(ApprovalTask)
        .filter(
            ApprovalTask.id == task_2_id
        )
        .first()
    )

    assert task_2 is not None

    assert task_2.status.value == "APPROVED"

    assert task_2.completed_at is not None


    # =========================================================
    # STEP 14 — VERIFY WORKFLOW COMPLETED
    # =========================================================

    db_session.expire_all()

    workflow_instance = (
        db_session.query(WorkflowInstance)
        .filter(
            WorkflowInstance.id == workflow_instance_id
        )
        .first()
    )

    assert workflow_instance is not None

    assert workflow_instance.status.value == "COMPLETED"

    assert workflow_instance.completed_at is not None


    # =========================================================
    # STEP 15 — VERIFY EXACTLY TWO APPROVAL TASKS EXIST
    # =========================================================

    approval_tasks = (
        db_session.query(ApprovalTask)
        .filter(
            ApprovalTask.workflow_instance_id
            == workflow_instance_id
        )
        .all()
    )

    assert len(approval_tasks) == 2

    assert all(
        task.status.value == "APPROVED"
        for task in approval_tasks
    )


def test_rejection_stops_workflow(
    client,
    db_session,
):
    """
    Verify that rejecting an approval task:

    1. Marks the task as REJECTED.
    2. Marks the workflow instance as REJECTED.
    3. Sets completed_at.
    4. Does not advance to Step 2.
    5. Does not create another approval task.
    """

    # =========================================================
    # STEP 1 — CREATE USER
    # =========================================================

    user_response = client.post(
        "/users",
        json={
            "name": "Rejection Test EMPLOYEE",
            "email": "rejection.EMPLOYEE@test.com",
            "role": "EMPLOYEE",
        },
    )

    assert user_response.status_code in (200, 201), (
        f"User creation failed: "
        f"{user_response.status_code} "
        f"{user_response.text}"
    )

    user_id = user_response.json()["id"]


    # =========================================================
    # STEP 2 — CREATE WORKFLOW DEFINITION
    # =========================================================

    workflow_response = client.post(
        "/workflow-definitions",
        json={
            "name": "Automated Rejection Workflow",
            "description": (
                "Two-step workflow used to test "
                "the rejection path."
            ),
        },
    )

    assert workflow_response.status_code in (200, 201), (
        f"Workflow creation failed: "
        f"{workflow_response.status_code} "
        f"{workflow_response.text}"
    )

    workflow_definition_id = (
        workflow_response.json()["id"]
    )


    # =========================================================
    # STEP 3 — CREATE STEP #1
    # =========================================================

    step_1_response = client.post(
        "/workflow-steps",
        json={
            "workflow_definition_id":
                workflow_definition_id,
            "step_order": 1,
            "step_name": "EMPLOYEE Approval",
            "approver_role": "EMPLOYEE",
            "is_required": True,
        },
    )

    assert step_1_response.status_code in (200, 201), (
        f"Step 1 creation failed: "
        f"{step_1_response.status_code} "
        f"{step_1_response.text}"
    )

    step_1_id = step_1_response.json()["id"]


    # =========================================================
    # STEP 4 — CREATE STEP #2
    # =========================================================

    step_2_response = client.post(
        "/workflow-steps",
        json={
            "workflow_definition_id":
                workflow_definition_id,
            "step_order": 2,
            "step_name": "Finance Approval",
            "approver_role": "EMPLOYEE",
            "is_required": True,
        },
    )

    assert step_2_response.status_code in (200, 201), (
        f"Step 2 creation failed: "
        f"{step_2_response.status_code} "
        f"{step_2_response.text}"
    )


    # =========================================================
    # STEP 5 — START WORKFLOW
    # =========================================================

    instance_response = client.post(
        "/workflow-instances",
        json={
            "workflow_definition_id":
                workflow_definition_id,
            "initiated_by": user_id,
        },
    )

    assert instance_response.status_code in (200, 201), (
        f"Workflow instance creation failed: "
        f"{instance_response.status_code} "
        f"{instance_response.text}"
    )

    workflow_instance_id = (
        instance_response.json()["id"]
    )


    # =========================================================
    # STEP 6 — FIND TASK #1
    # =========================================================

    db_session.expire_all()

    task_1 = (
        db_session.query(ApprovalTask)
        .filter(
            ApprovalTask.workflow_instance_id
            == workflow_instance_id,
            ApprovalTask.workflow_step_id
            == step_1_id,
        )
        .first()
    )

    assert task_1 is not None

    assert task_1.status.value == "PENDING"

    task_1_id = task_1.id


    # =========================================================
    # STEP 7 — REJECT TASK #1
    # =========================================================

    reject_response = client.post(
        f"/approval-tasks/{task_1_id}/reject",
        json={
            "comments": (
                "Expense rejected during "
                "automated workflow test."
            )
        },
    )

    assert reject_response.status_code in (
        200,
        201,
    ), (
        f"Task rejection failed: "
        f"{reject_response.status_code} "
        f"{reject_response.text}"
    )


    # =========================================================
    # STEP 8 — VERIFY TASK #1 IS REJECTED
    # =========================================================

    db_session.expire_all()

    rejected_task = (
        db_session.query(ApprovalTask)
        .filter(
            ApprovalTask.id == task_1_id
        )
        .first()
    )

    assert rejected_task is not None

    assert rejected_task.status.value == "REJECTED"

    assert rejected_task.completed_at is not None


    # =========================================================
    # STEP 9 — VERIFY WORKFLOW IS REJECTED
    # =========================================================

    db_session.expire_all()

    workflow_instance = (
        db_session.query(WorkflowInstance)
        .filter(
            WorkflowInstance.id
            == workflow_instance_id
        )
        .first()
    )

    assert workflow_instance is not None

    assert workflow_instance.status.value == "REJECTED"

    assert workflow_instance.completed_at is not None


    # =========================================================
    # STEP 10 — VERIFY WORKFLOW DID NOT ADVANCE
    # =========================================================

    assert workflow_instance.current_step_order == 1


    # =========================================================
    # STEP 11 — VERIFY NO TASK #2 WAS CREATED
    # =========================================================

    approval_tasks = (
        db_session.query(ApprovalTask)
        .filter(
            ApprovalTask.workflow_instance_id
            == workflow_instance_id
        )
        .all()
    )

    assert len(approval_tasks) == 1

    assert approval_tasks[0].id == task_1_id

    assert approval_tasks[0].status.value == "REJECTED"

def test_processed_task_cannot_be_processed_again(
    client,
    db_session,
):
    """
    Verify that once an approval task has been processed:

    1. It cannot be approved again.
    2. It cannot be rejected after approval.
    3. Its original APPROVED state remains unchanged.
    4. The workflow does not become corrupted.
    """

    # =========================================================
    # STEP 1 — CREATE USER
    # =========================================================

    user_response = client.post(
        "/users",
        json={
            "name": "Duplicate Processing EMPLOYEE",
            "email": "duplicate.EMPLOYEE@test.com",
            "role": "EMPLOYEE",
        },
    )

    assert user_response.status_code in (200, 201), (
        f"User creation failed: "
        f"{user_response.status_code} "
        f"{user_response.text}"
    )

    user_id = user_response.json()["id"]


    # =========================================================
    # STEP 2 — CREATE WORKFLOW DEFINITION
    # =========================================================

    workflow_response = client.post(
        "/workflow-definitions",
        json={
            "name": "Duplicate Processing Workflow",
            "description": (
                "Workflow used to verify that an "
                "approval task cannot be processed twice."
            ),
        },
    )

    assert workflow_response.status_code in (200, 201), (
        f"Workflow creation failed: "
        f"{workflow_response.status_code} "
        f"{workflow_response.text}"
    )

    workflow_definition_id = (
        workflow_response.json()["id"]
    )


    # =========================================================
    # STEP 3 — CREATE ONLY ONE WORKFLOW STEP
    # =========================================================

    step_response = client.post(
        "/workflow-steps",
        json={
            "workflow_definition_id":
                workflow_definition_id,
            "step_order": 1,
            "step_name": "EMPLOYEE Approval",
            "approver_role": "EMPLOYEE",
            "is_required": True,
        },
    )

    assert step_response.status_code in (200, 201), (
        f"Workflow step creation failed: "
        f"{step_response.status_code} "
        f"{step_response.text}"
    )

    step_id = step_response.json()["id"]


    # =========================================================
    # STEP 4 — START WORKFLOW INSTANCE
    # =========================================================

    instance_response = client.post(
        "/workflow-instances",
        json={
            "workflow_definition_id":
                workflow_definition_id,
            "initiated_by": user_id,
        },
    )

    assert instance_response.status_code in (200, 201), (
        f"Workflow instance creation failed: "
        f"{instance_response.status_code} "
        f"{instance_response.text}"
    )

    workflow_instance_id = (
        instance_response.json()["id"]
    )


    # =========================================================
    # STEP 5 — FIND INITIAL APPROVAL TASK
    # =========================================================

    db_session.expire_all()

    approval_task = (
        db_session.query(ApprovalTask)
        .filter(
            ApprovalTask.workflow_instance_id
            == workflow_instance_id,
            ApprovalTask.workflow_step_id
            == step_id,
        )
        .first()
    )

    assert approval_task is not None

    assert approval_task.status.value == "PENDING"

    approval_task_id = approval_task.id


    # =========================================================
    # STEP 6 — APPROVE TASK SUCCESSFULLY
    # =========================================================

    first_approval_response = client.post(
        f"/approval-tasks/{approval_task_id}/approve",
        json={
            "comments": (
                "First valid approval."
            )
        },
    )

    assert first_approval_response.status_code in (
        200,
        201,
    ), (
        f"Initial approval failed: "
        f"{first_approval_response.status_code} "
        f"{first_approval_response.text}"
    )


    # =========================================================
    # STEP 7 — VERIFY TASK IS APPROVED
    # =========================================================

    db_session.expire_all()

    approval_task = (
        db_session.query(ApprovalTask)
        .filter(
            ApprovalTask.id
            == approval_task_id
        )
        .first()
    )

    assert approval_task is not None

    assert approval_task.status.value == "APPROVED"

    assert approval_task.completed_at is not None


    # =========================================================
    # STEP 8 — VERIFY SINGLE-STEP WORKFLOW COMPLETED
    # =========================================================

    db_session.expire_all()

    workflow_instance = (
        db_session.query(WorkflowInstance)
        .filter(
            WorkflowInstance.id
            == workflow_instance_id
        )
        .first()
    )

    assert workflow_instance is not None

    assert workflow_instance.status.value == "COMPLETED"

    assert workflow_instance.completed_at is not None


    # =========================================================
    # STEP 9 — TRY TO APPROVE SAME TASK AGAIN
    # =========================================================

    duplicate_approval_response = client.post(
        f"/approval-tasks/{approval_task_id}/approve",
        json={
            "comments": (
                "This duplicate approval "
                "must be rejected."
            )
        },
    )

    assert duplicate_approval_response.status_code == 400, (
        "Expected duplicate approval to return 400, "
        f"but received "
        f"{duplicate_approval_response.status_code}: "
        f"{duplicate_approval_response.text}"
    )


    # =========================================================
    # STEP 10 — TRY TO REJECT ALREADY APPROVED TASK
    # =========================================================

    duplicate_rejection_response = client.post(
        f"/approval-tasks/{approval_task_id}/reject",
        json={
            "comments": (
                "Attempting to reject an "
                "already approved task."
            )
        },
    )

    assert duplicate_rejection_response.status_code == 400, (
        "Expected rejection of processed task "
        "to return 400, "
        f"but received "
        f"{duplicate_rejection_response.status_code}: "
        f"{duplicate_rejection_response.text}"
    )


    # =========================================================
    # STEP 11 — VERIFY TASK STATE DID NOT CHANGE
    # =========================================================

    db_session.expire_all()

    final_task = (
        db_session.query(ApprovalTask)
        .filter(
            ApprovalTask.id
            == approval_task_id
        )
        .first()
    )

    assert final_task is not None

    assert final_task.status.value == "APPROVED"

    assert final_task.completed_at is not None


    # =========================================================
    # STEP 12 — VERIFY WORKFLOW REMAINS COMPLETED
    # =========================================================

    db_session.expire_all()

    final_workflow = (
        db_session.query(WorkflowInstance)
        .filter(
            WorkflowInstance.id
            == workflow_instance_id
        )
        .first()
    )

    assert final_workflow is not None

    assert final_workflow.status.value == "COMPLETED"

    assert final_workflow.completed_at is not None


    # =========================================================
    # STEP 13 — VERIFY NO DUPLICATE TASK WAS CREATED
    # =========================================================

    approval_tasks = (
        db_session.query(ApprovalTask)
        .filter(
            ApprovalTask.workflow_instance_id
            == workflow_instance_id
        )
        .all()
    )

    assert len(approval_tasks) == 1

    assert approval_tasks[0].id == approval_task_id

    assert approval_tasks[0].status.value == "APPROVED"


def test_transaction_failure_rolls_back_all_changes(
    client,
    db_session,
):
    """
    Verify transaction atomicity.

    Scenario:

    1. Create a two-step workflow.
    2. Start the workflow.
    3. Task #1 is initially PENDING.
    4. Attempt to approve Task #1.
    5. Force ApprovalTaskRepository.add() to fail
       while creating Task #2.
    6. Verify the entire transaction is rolled back.

    Expected final state:

        Task #1       -> PENDING
        Workflow      -> still Step 1
        Workflow      -> not COMPLETED
        Task #2       -> does not exist

    This proves that partial workflow state is not
    committed when next-task creation fails.
    """

    # =========================================================
    # STEP 1 — CREATE USER
    # =========================================================

    user_response = client.post(
        "/users",
        json={
            "name": "Rollback Test EMPLOYEE",
            "email": "rollback.EMPLOYEE@test.com",
            "role": "EMPLOYEE",
        },
    )

    assert user_response.status_code in (200, 201), (
        f"User creation failed: "
        f"{user_response.status_code} "
        f"{user_response.text}"
    )

    user_id = user_response.json()["id"]

    assert user_id is not None


    # =========================================================
    # STEP 2 — CREATE WORKFLOW DEFINITION
    # =========================================================

    workflow_response = client.post(
        "/workflow-definitions",
        json={
            "name": "Transaction Rollback Workflow",
            "description": (
                "Two-step workflow used to verify "
                "atomic transaction rollback."
            ),
        },
    )

    assert workflow_response.status_code in (200, 201), (
        f"Workflow definition creation failed: "
        f"{workflow_response.status_code} "
        f"{workflow_response.text}"
    )

    workflow_definition_id = (
        workflow_response.json()["id"]
    )

    assert workflow_definition_id is not None


    # =========================================================
    # STEP 3 — CREATE WORKFLOW STEP #1
    # =========================================================

    step_1_response = client.post(
        "/workflow-steps",
        json={
            "workflow_definition_id":
                workflow_definition_id,
            "step_order": 1,
            "step_name": "EMPLOYEE Approval",
            "approver_role": "EMPLOYEE",
            "is_required": True,
        },
    )

    assert step_1_response.status_code in (200, 201), (
        f"Step #1 creation failed: "
        f"{step_1_response.status_code} "
        f"{step_1_response.text}"
    )

    step_1_id = step_1_response.json()["id"]

    assert step_1_id is not None


    # =========================================================
    # STEP 4 — CREATE WORKFLOW STEP #2
    # =========================================================

    step_2_response = client.post(
        "/workflow-steps",
        json={
            "workflow_definition_id":
                workflow_definition_id,
            "step_order": 2,
            "step_name": "Finance Approval",
            "approver_role": "EMPLOYEE",
            "is_required": True,
        },
    )

    assert step_2_response.status_code in (200, 201), (
        f"Step #2 creation failed: "
        f"{step_2_response.status_code} "
        f"{step_2_response.text}"
    )

    step_2_id = step_2_response.json()["id"]

    assert step_2_id is not None


    # =========================================================
    # STEP 5 — START WORKFLOW INSTANCE
    # =========================================================

    instance_response = client.post(
        "/workflow-instances",
        json={
            "workflow_definition_id":
                workflow_definition_id,
            "initiated_by": user_id,
        },
    )

    assert instance_response.status_code in (200, 201), (
        f"Workflow instance creation failed: "
        f"{instance_response.status_code} "
        f"{instance_response.text}"
    )

    workflow_instance_id = (
        instance_response.json()["id"]
    )

    assert workflow_instance_id is not None


    # =========================================================
    # STEP 6 — FIND INITIAL APPROVAL TASK #1
    # =========================================================

    db_session.expire_all()

    task_1 = (
        db_session.query(ApprovalTask)
        .filter(
            ApprovalTask.workflow_instance_id
            == workflow_instance_id,
            ApprovalTask.workflow_step_id
            == step_1_id,
        )
        .first()
    )

    assert task_1 is not None, (
        "Initial ApprovalTask #1 was not created."
    )

    assert task_1.status.value == "PENDING"

    task_1_id = task_1.id


    # =========================================================
    # STEP 7 — VERIFY INITIAL WORKFLOW STATE
    # =========================================================

    db_session.expire_all()

    workflow_before_failure = (
        db_session.query(WorkflowInstance)
        .filter(
            WorkflowInstance.id
            == workflow_instance_id
        )
        .first()
    )

    assert workflow_before_failure is not None

    assert (
        workflow_before_failure.current_step_order
        == 1
    )

    assert (
        workflow_before_failure.status.value
        != "COMPLETED"
    )

    assert (
        workflow_before_failure.completed_at
        is None
    )


    # =========================================================
    # STEP 8 — FORCE NEXT TASK CREATION TO FAIL
    # =========================================================
    #
    # approve_task() should:
    #
    # Task #1 -> APPROVED
    # Workflow -> Step 2
    # Try to add Task #2
    #
    # We deliberately make add() raise an exception.
    #
    # The service should catch the exception and execute:
    #
    # self.db.rollback()
    #
    # Therefore NONE of those intermediate changes
    # should survive.
    # =========================================================

    with patch(
        "app.repositories.approval_task_repository."
        "ApprovalTaskRepository.add",
        side_effect=RuntimeError(
            "Simulated next-task creation failure"
        ),
    ):
        response = client.post(
            f"/approval-tasks/{task_1_id}/approve",
            json={
                "comments": (
                    "This approval intentionally "
                    "triggers transaction rollback."
                )
            },
        )


    # =========================================================
    # STEP 9 — VERIFY API REPORTED SERVER FAILURE
    # =========================================================

    assert response.status_code == 500, (
        "Expected HTTP 500 from simulated failure, "
        f"but received {response.status_code}: "
        f"{response.text}"
    )


    # =========================================================
    # STEP 10 — RESET CURRENT SQLALCHEMY SESSION STATE
    # =========================================================
    #
    # expire_all() ensures subsequent queries read fresh
    # state from PostgreSQL instead of using cached ORM state.
    # =========================================================

    db_session.rollback()

    db_session.expire_all()


    # =========================================================
    # STEP 11 — VERIFY TASK #1 WAS ROLLED BACK
    # =========================================================

    task_1_after_failure = (
        db_session.query(ApprovalTask)
        .filter(
            ApprovalTask.id
            == task_1_id
        )
        .first()
    )

    assert task_1_after_failure is not None

    assert (
        task_1_after_failure.status.value
        == "PENDING"
    ), (
        "Task #1 should have rolled back to PENDING."
    )

    assert (
        task_1_after_failure.completed_at
        is None
    ), (
        "Task #1 completed_at should remain NULL "
        "after rollback."
    )


    # =========================================================
    # STEP 12 — VERIFY WORKFLOW STATE WAS ROLLED BACK
    # =========================================================

    db_session.expire_all()

    workflow_after_failure = (
        db_session.query(WorkflowInstance)
        .filter(
            WorkflowInstance.id
            == workflow_instance_id
        )
        .first()
    )

    assert workflow_after_failure is not None

    assert (
        workflow_after_failure.current_step_order
        == 1
    ), (
        "Workflow should remain at Step 1 "
        "after transaction rollback."
    )

    assert (
        workflow_after_failure.status.value
        != "COMPLETED"
    ), (
        "Workflow must not become COMPLETED "
        "after transaction failure."
    )

    assert (
        workflow_after_failure.completed_at
        is None
    ), (
        "Workflow completed_at must remain NULL "
        "after transaction rollback."
    )


    # =========================================================
    # STEP 13 — VERIFY TASK #2 DOES NOT EXIST
    # =========================================================

    db_session.expire_all()

    task_2 = (
        db_session.query(ApprovalTask)
        .filter(
            ApprovalTask.workflow_instance_id
            == workflow_instance_id,
            ApprovalTask.workflow_step_id
            == step_2_id,
        )
        .first()
    )

    assert task_2 is None, (
        "Task #2 must not exist because its creation "
        "failed and the transaction should have rolled back."
    )


    # =========================================================
    # STEP 14 — VERIFY EXACTLY ONE TASK EXISTS
    # =========================================================

    all_tasks = (
        db_session.query(ApprovalTask)
        .filter(
            ApprovalTask.workflow_instance_id
            == workflow_instance_id
        )
        .all()
    )

    assert len(all_tasks) == 1, (
        "Exactly one approval task should exist "
        "after rollback."
    )

    assert all_tasks[0].id == task_1_id

    assert (
        all_tasks[0].status.value
        == "PENDING"
    )