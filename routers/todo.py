"""Todo routes for the REST API."""

from fastapi import APIRouter, HTTPException, Request, Response

from src.models import Todo, TodoCreate
from src.persistence import TodoDao

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
    return _dao.get_all()


@router.post("/", response_model=Todo, status_code=201)
def create_todo(todo: TodoCreate, request: Request, response: Response):
    """Create and save a new todo. A unique ID is assigned."""
    created = _dao.save(todo)
    # Return the location of the new todo.
    location = f"/todos/{created.id}"
    # A cleaner way to get the location URL is reverse mapping.
    # location = request.url_for("get_todo", todo_id=str(created.id))
    response.headers["Location"] = location
    return created


@router.get("/{todo_id}", response_model=Todo)
def get_todo(todo_id: int):
    """Get a specific todo by id.

    :param todo_id: identifier of the todo to get.
    """
    todo = _dao.get(todo_id)
    if not todo:
        raise HTTPException(status_code=404, detail="Todo not found")
    return todo


@router.put("/{todo_id}", response_model=Todo)
def update_todo(todo_id: int, todo: TodoCreate):
    """Update an existing Todo.

    :param todo_id: identifier of the todo to update
    :param todo: revised data for the todo
    """
    existing = _dao.get(todo_id)
    if not existing:
        raise HTTPException(status_code=404, detail="Todo not found")

    updated = Todo(
        id=todo_id,
        text=todo.text,
        done=todo.done,
    )
    return _dao.update(updated)


@router.delete("/{todo_id}", status_code=204)
def delete_todo(todo_id: int):
    """Delete a Todo.

    :param todo_id: identifier of the todo to delete
    
    Returns 204 No Content on success.
    Returns 404 if todo is not found.
    """
    todo = _dao.get(todo_id)
    if not todo:
        raise HTTPException(status_code=404, detail="Todo not found")
    
    _dao.delete(todo_id)
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
