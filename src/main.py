"""FastAPI implementation of the Todo REST API."""

import os
from pathlib import Path

from fastapi import FastAPI

from src import logging_config
from src.persistence import TodoDao
from routers import todo

logging_config.configure_logging()


# Data Access Object (dao) provides persistence operations for todo.
default_data_dir = Path(__file__).resolve().parent / "data"
todo_data_dir = Path(os.getenv("TODO_DATA_DIR", str(default_data_dir)))
dao = TodoDao(str(todo_data_dir / "todo_data.json"))

# 'app' is refers to FastAPI
# use param: redirect_slashes=False to disable automatic
# redirection of paths without trailing slash.
api_root_path = os.getenv("API_ROOT_PATH", "")
app = FastAPI(root_path=api_root_path)

# Set the DAO instance for the todo router
todo.set_dao(dao)

# Include the todo router
app.include_router(todo.router)
