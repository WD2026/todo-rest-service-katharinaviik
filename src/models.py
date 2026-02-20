"""Models for object serialization and data validation in the app.

Define Pydantic models for Todo items and Todo creation requests.
Pydantic is a library for data validation and serialization using
Python type annoatations. It is often used with FastAPI and SqlAlchemy..
"""
from pydantic import BaseModel, field_validator

MIN_TEXT_LENGTH = 2


class TodoCreate(BaseModel):
    """Information required to create a new Todo item.
    
    The application will assign an ID when the Todo is created.
    """
    text: str
    done: bool = False

    @field_validator("text")
    def validate_text(cls, v: str) -> str:
        """Ensure `text` field is at least MIN_TEXT_LENGTH characters and not blank."""
        if not isinstance(v, str):
            raise TypeError("text must be a string")
        v = v.strip()
        if len(v) < MIN_TEXT_LENGTH:
            raise ValueError(f"text must be at least {MIN_TEXT_LENGTH} characters long")
        return v


class Todo(TodoCreate):
    """A Todo item with an ID."""
    id: int
    # other fields inherited from TodoCreate
