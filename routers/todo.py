"""Todo routes for the REST API."""

from fastapi import APIRouter, HTTPException, Request, Response

from src.logging_config import get_logger
from src.models import Todo, TodoCreate
from src.persistence import TodoDao

logger = get_logger(__name__)

# This will be set by main.py
_dao: TodoDao = None


def set_dao(dao: TodoDao):
    """Set the TodoDao instance for this router."""
    global _dao
    _dao = dao


router = APIRouter(prefix="/todos", tags=["Todos"])


@router.get("/", response_model=list[Todo])
def get_todos():
    """Get all todos."""
    todos = _dao.get_all()
    logger.info("Todos retrieved", count=len(todos))
    return todos


@router.post("/", response_model=Todo, status_code=201)
def create_todo(todo: TodoCreate, request: Request, response: Response):
    """Create and save a new todo. A unique ID is assigned."""
    created = _dao.save(todo)
    response.headers["Location"] = request.url_for("get_todo", todo_id=str(created.id)).path
    logger.info("Todo created", todo_id=created.id)
    return created


@router.get("/{todo_id}", response_model=Todo, name="get_todo")
def get_todo(todo_id: int):
    """Get a specific todo by id.

    :param todo_id: identifier of the todo to get.
    """
    todo = _dao.get(todo_id)
    if not todo:
        logger.warning("Todo not found", todo_id=todo_id)
        raise HTTPException(status_code=404, detail="Todo not found")
    logger.info("Todo retrieved", todo_id=todo_id)
    return todo


@router.put("/{todo_id}", response_model=Todo)
def update_todo(todo_id: int, todo: TodoCreate):
    """Update an existing Todo.

    :param todo_id: identifier of the todo to update
    :param todo: revised data for the todo
    """
    existing = _dao.get(todo_id)
    if not existing:
        logger.warning("Todo not found", todo_id=todo_id)
        raise HTTPException(status_code=404, detail="Todo not found")

    updated = Todo(
        id=todo_id,
        text=todo.text,
        done=todo.done,
    )
    result = _dao.update(updated)
    logger.info("Todo updated", todo_id=todo_id)
    return result


@router.delete("/{todo_id}", status_code=204)
def delete_todo(todo_id: int):
    """Delete a Todo.

    :param todo_id: identifier of the todo to delete
    
    Returns 204 No Content on success.
    Returns 404 if todo is not found.
    """
    todo = _dao.get(todo_id)
    if not todo:
        logger.warning("Todo not found", todo_id=todo_id)
        raise HTTPException(status_code=404, detail="Todo not found")
    
    _dao.delete(todo_id)
    logger.info("Todo deleted", todo_id=todo_id)
    # Return 204 No Content with no body


@router.options("/", response_class=Response, responses={200: {"description": "Allowed methods for todos collection", "content": {"application/json": {"schema": {"type": "object"}, "example": {}}}, "headers": {"Allow": {"schema": {"type": "string"}, "description": "Comma-separated list of allowed methods"}}}})
def todos_options():
    """Return the allowed HTTP methods for the todos collection.
    
    Per REST spec, OPTIONS returns capabilities, not data.
    The Allow header lists all supported methods.
    """
    return Response(content="{}", status_code=200, media_type="application/json", headers={"Allow": "GET,POST,OPTIONS"})


@router.options("/{todo_id}", response_class=Response, responses={200: {"description": "Allowed methods for a single todo", "content": {"application/json": {"schema": {"type": "object"}, "example": {}}}, "headers": {"Allow": {"schema": {"type": "string"}, "description": "Comma-separated list of allowed methods"}}}})
def todo_options(todo_id: int):
    """Return the allowed HTTP methods for a single todo.
    
    Per REST spec, OPTIONS returns capabilities (Allow header), not the resource data.
    Does not validate whether the todo exists.
    
    :param todo_id: identifier of the todo (not validated)
    """
    return Response(content="{}", status_code=200, media_type="application/json", headers={"Allow": "GET,PUT,DELETE,OPTIONS"})
