"""A Data Access Object (DAO) for CRUD operations on Todo items.

Implements thread-safe file-based persistence using JSON.
"""
import json
import logging
import os
from threading import RLock
from typing import Dict, Iterable

from src.models import Todo, TodoCreate


class TodoDao:
    """Persistence operations for Todo items.

    Args:
        filename (str): The JSON file to use for storage.
        If the file does not exist, it will be created.
    Methods:
        get(todo_id: int) -> Todo|None: Get a Todo by id.
        get_all() -> list[Todo]:        Get all Todo items.
        save(new_todo: TodoCreate) -> Todo: Save a new Todo.
        update(todo: Todo) -> None:     Update an existing Todo.
        delete(todo_id: int) -> None:   Delete a Todo by id.
    """
    def __init__(self, filename: str):
        self.filename = filename
        self.lock = RLock()
        # read todos into memory.
        self.todos = self._read_all()

    def _read_all(self) -> Dict[int, Todo]:
        """Read all Todo items from a JSON file.

        :return: A dict of Todo items, keyed by Todo id.
        """
        todos: Dict[int, Todo] = {}
        if not os.path.exists(self.filename):
            logger = logging.getLogger(__name__)
            logger.warning(f"Todo data file '{self.filename}' not found. "
                           "Returning an empty todo list.")
            return todos
        with self.lock:
            with open(self.filename, "r") as file:
                for todo_data in json.load(file):
                    todo_id = todo_data["id"]
                    # Use Pydantic to validate and instantiate the model.
                    todos[todo_id] = Todo.model_validate(todo_data)
                    # for a flexible schema, do this instead:
                    # todos[todo_id] = Todo(**todo_data)
                return todos

    def _write_all(self, todos: Iterable[Todo]) -> None:
        """Write all Todo items to the JSON file."""
        # TODO: should write to a temp file and then rename to avoid data loss.
        with self.lock:
            with open(self.filename, "w") as f:
                # Convert Pydantic Todo models to plain dicts before dumping.
                serializable = [t.model_dump() for t in todos]
                json.dump(serializable, f, indent=2)

    def _next_id(self) -> int:
        """Generates an available id for a new Todo.

        :return: An integer id not currently used by any Todo.
        """
        if not self.todos:
            return 1
        # the todo keys are the ids
        return max(self.todos.keys()) + 1

    def get(self, todo_id: int) -> Todo | None:
        """Get a Todo by its id.

        :return: The Todo with the given id, or None if not found.
        """
        return self.todos.get(todo_id, None)

    def get_all(self) -> list[Todo]:
        """Get all Todo items."""
        return list(self.todos.values())

    def save(self, todo_create: TodoCreate) -> Todo:
        """Save a new Todo and assign it an id.

        :param todo_create: a TodoCreate object with info for the new Todo.
        :return: The created Todo with its assigned id.
        """
        with self.lock:
            todo_id = self._next_id()
            # model_dump is provided by Pydantic Model class.
            todo = Todo(id=todo_id, **todo_create.model_dump())
            self.todos[todo_id] = todo
            # terribly inefficient but write all todos each time.
            self._write_all(list(self.todos.values()))
        return todo

    def update(self, todo: Todo) -> Todo:
        """Update an existing Todo."""
        todo_id = todo.id
        if todo_id not in self.todos:
            raise ValueError(f"Todo id {todo.id} not found")
        self.todos[todo_id] = todo
        self._write_all(list(self.todos.values()))
        return todo

    def delete(self, todo_id: int) -> None:
        """Delete a Todo by its id."""
        if todo_id not in self.todos:
            raise ValueError(f"Todo id {todo_id} not found")
        del self.todos[todo_id]
        self._write_all(list(self.todos.values()))
