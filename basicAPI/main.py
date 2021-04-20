from fastapi import FastAPI
from pydantic import BaseModel
from tortoise.contrib.pydantic import pydantic_model_creator
from tortoise.contrib.fastapi import register_tortoise
from models import Todo

app = FastAPI()

# before you can create a database, just like in flutter, 
# you need a model from whele to map data to this is created 
# using pydantic BaseModel class. You can then specify the data 
# types uisng typehints
class CreateTodo(BaseModel):
    name: str
    description: str

# we can also create our own pydantic model using
#   tortoise, using this, we dont need our custom BaseModel any more
todo_pydantic = pydantic_model_creator(Todo, name = "Todo")
todo_pydanticIn = pydantic_model_creator(Todo, name = "TodoIn", exclude_readonly = True)

todos = []

@app.get('/todo')
async def get_todos():
    todos = await todo_pydantic.from_queryset(Todo.all())
    return {'status': 'ok', 'data' : todos}

@app.get('/todo/{todo_id}')
async def get_todo(todo_id:int):
    todo = await todo_pydantic.from_queryset_single(Todo.get(id = todo_id))
    return {'status': 'ok', 'data' : todo}

@app.delete('/todo/{todo_id}')
async def delete_todo(todo_id: int):
    await Todo.filter(id = todo_id).delete()
    return {}

@app.post('/todo')
async def create_todo(todo: todo_pydanticIn):
    print(todo.json())
    # exclude_unset will deal with null collumns if the user does not pass it in
    todo_obj = await Todo.create(**todo.dict(exclude_unset = True))
    response = await todo_pydantic.from_tortoise_orm(todo_obj)
    return {'status' : 'ok', 'data' : response}


register_tortoise(
    app,
    db_url='sqlite://db.sqlite3',
    modules={'models': ['models']},
    generate_schemas = True,
    add_exception_handlers = True
)
