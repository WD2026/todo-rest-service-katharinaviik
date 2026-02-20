import pytest

from persistence import TodoDao
from models import TodoCreate, Todo


def test_save_and_get(tmp_path, monkeypatch):
    file = tmp_path / "todos.json"
    dao = TodoDao(str(file))

    writes = []

    def fake_write(self, todos):
        writes.append([t.model_dump() for t in todos])

    monkeypatch.setattr(TodoDao, "_write_all", fake_write)

    tc = TodoCreate(text="First")
    todo = dao.save(tc)

    assert todo.id == 1
    assert todo.text == "First"
    assert todo.done is False
    assert dao.get(1).id == 1
    assert len(writes) == 1
    assert writes[0][0]["id"] == 1


def test_get_all_and_multiple_saves(tmp_path, monkeypatch):
    file = tmp_path / "todos.json"
    dao = TodoDao(str(file))

    def noop_write(self, todos):
        # no-op to avoid JSON serialization of Pydantic models
        return None

    monkeypatch.setattr(TodoDao, "_write_all", noop_write)

    t1 = dao.save(TodoCreate(text="First"))
    t2 = dao.save(TodoCreate(text="Second"))

    all_todos = dao.get_all()
    ids = {t.id for t in all_todos}
    assert ids == {1, 2}
    assert t1.id == 1 and t2.id == 2


def test_update_existing_and_missing(tmp_path, monkeypatch):
    file = tmp_path / "todos.json"
    dao = TodoDao(str(file))

    monkeypatch.setattr(TodoDao, "_write_all", lambda self, todos: None)

    saved = dao.save(TodoCreate(text="Do it"))
    saved.done = True
    dao.update(saved)

    got = dao.get(saved.id)
    assert got is not None and got.done is True

    # update missing should raise
    with pytest.raises(ValueError):
        dao.update(Todo(id=999, text="X", done=False))


def test_delete_existing_and_missing(tmp_path, monkeypatch):
    file = tmp_path / "todos.json"
    dao = TodoDao(str(file))

    monkeypatch.setattr(TodoDao, "_write_all", lambda self, todos: None)

    saved = dao.save(TodoCreate(text="Temp"))
    dao.delete(saved.id)
    assert dao.get(saved.id) is None

    with pytest.raises(ValueError):
        dao.delete(saved.id)
