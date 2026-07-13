# Common Parent class for all Models

from sqlalchemy.orm import DeclarativeBase


class Base(DeclarativeBase):
    pass


# Import models AFTER Base creation
from app.models.user import User
from app.models.workflow_definition import WorkflowDefinition
from app.models.workflow_step import WorkflowStep