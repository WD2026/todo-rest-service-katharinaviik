[![Review Assignment Due Date](https://classroom.github.com/assets/deadline-readme-button-22041afd0340ce965d47ae6ef1cefeee28c7c493a6346c4f15d667ab976d596c.svg)](https://classroom.github.com/a/GESDgYQ7)
[![Open in Codespaces](https://classroom.github.com/assets/launch-codespace-2972f46106e565e64193e422d61a12cf1da4916b45550586e14ef0a7c637dd04.svg)](https://classroom.github.com/open-in-codespaces?assignment_repo_id=22443844)
## Todo REST Service
````markdown
## Todo REST Service

A RESTful web service using FastAPI.
The service handles HTTP GET, POST, UPDATE, DELETE, and OPTIONS
methods for a "/todo" endpoint.

### Code Organization

| File                 | Contents           |
|:---------------------|:-------------------|
| `src/models.py`          | Classes for Todo and TodoCreate. Used for serialization and input validation. |
| `src/persistence.py`     | Simple persistence of Todo objects. |
| `src/main.py`            | FastAPI code to run the application. |

## How to Build and Run

1. Install required packages in a virtual env.
   You can also create a venv in VS Code, which may be easier.
   ```shell
   $ python -m venv env
   # Activate the venv. This is for Linux & MacOS.  
   . env/bin/activate
   (env)$ pip install -r requirements.txt
   ```

2. Run the app using uvicorn:
   ```shell
   (env)$ uvicorn src.main:app --reload
   ```

3. Navigate to <http://127.0.0.1:8000/docs>. (Sorry, no html UI yet.)

   - You should see OpenAPI style documentation of the endpoints.
   - Click the "try it" button to input values and submit a request.

4. Stop the application by pressing CTRL-C or close the window.

## Class Diagram

The class hierarchy for the Pydantic models is:

```mermaid
classDiagram
    class BaseModel
    class TodoCreate
    class Todo

    BaseModel <|-- TodoCreate
    TodoCreate <|-- Todo
```