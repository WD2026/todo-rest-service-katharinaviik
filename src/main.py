"""FastAPI implementation of the Todo REST API."""

from pathlib import Path

from fastapi import FastAPI

from src.persistence import TodoDao
from routers import todo


# Data Access Object (dao) provides persistence operations for todo.
dao = TodoDao(str(Path(__file__).with_name("todo_data.json")))

# 'app' is refers to FastAPI
# use param: redirect_slashes=False to disable automatic
# redirection of paths without trailing slash.
app = FastAPI(title="Todo REST API")

# Set the DAO instance for the todo router
todo.set_dao(dao)

# Include the todo router
app.include_router(todo.router)
