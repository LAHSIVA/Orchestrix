from enum import Enum


class UserRole(str, Enum):
    EMPLOYEE = "EMPLOYEE"
    APPROVER = "APPROVER"
    WORKFLOW_ADMIN = "WORKFLOW_ADMIN"
    AUDITOR = "AUDITOR"


class UserStatus(str, Enum):
    ACTIVE = "ACTIVE"
    INACTIVE = "INACTIVE"