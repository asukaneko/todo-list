from flask import Flask, jsonify, request, send_from_directory
from flask_pydantic import validate
from pydantic import BaseModel, Field
from tinydb import TinyDB, Query
from datetime import datetime
import os

app = Flask(__name__)
CORS = lambda app: app  
from flask_cors import CORS
CORS(app)

# 数据库
DB_FILE = "db.json"
db = TinyDB(DB_FILE)
TodoTable = db.table("todos")
q = Query()

# 工具
def now_ts() -> int:
    return int(datetime.now().timestamp())

def next_id() -> int:
    ids = sorted([t["id"] for t in TodoTable.all()])
    expected_id = 1
    for id in ids:
        if id == expected_id:
            expected_id += 1
        elif id > expected_id:
            break
    return expected_id

def ok(message="ok", **kwargs):
    return jsonify({"code": 200, "message": message, **kwargs})

def fail(message="Invalid input", code=400):
    return jsonify({"code": code, "message": message}), code

# ---------- Schema ----------
class TodoOut(BaseModel):
    id: int
    title: str
    completed: bool
    created_at: int
    updated_at: int

class TodoCreateForm(BaseModel):
    title: str = Field(..., min_length=1)

class TodoUpdateStatusBody(BaseModel):
    completed: bool

class TodoUpdateTitleBody(BaseModel):
    title: str = Field(..., min_length=1)

# 修改静态文件路由配置
@app.route('/assets/<path:filename>')
def serve_assets(filename):
    "提供assets目录下的静态文件"
    assets_dir = os.path.join(os.path.dirname(__file__), 'assets')
    return send_from_directory(assets_dir, filename)

@app.route('/')
def index():
    "提供首页"
    return send_from_directory(os.path.dirname(__file__), "index.html")

# ---------- 1. 获取所有待办 ----------
@app.get("/api/todos")
def list_todos():
    todos = TodoTable.all()
    return ok("ok", todos_list=todos)

# ---------- 2. 新增一个待办（JSON格式） ----------
@app.post("/api/todos")
def add_todo():
    if not request.json or 'title' not in request.json:
        return fail("请求体中缺少title字段")
    
    title = request.json.get("title", "").strip()
    if not title:
        return fail("title 不能为空")
    
    todo = {
        "id": next_id(),
        "title": title,
        "completed": False,
        "created_at": now_ts(),
        "updated_at": now_ts(),
    }
    TodoTable.insert(todo)
    return ok("Created", data=todo) 

# ---------- 3. 获取单个待办 ----------
@app.get("/api/todos/<int:todo_id>")
def get_todo(todo_id: int):
    todo = TodoTable.get(q.id == todo_id)
    if not todo:
        return fail("Not Found", code=404) 
    return ok("ok", data=todo)

# ---------- 4. 删除指定待办 ----------
@app.delete("/api/todos/<int:todo_id>")
def delete_todo(todo_id: int):
    if not TodoTable.contains(q.id == todo_id):
        return fail() 
    TodoTable.remove(q.id == todo_id)
    return ok("ok")

# ---------- 5. 更新完成状态 ----------
@app.put("/api/todos/<int:todo_id>/status")
@validate(body=TodoUpdateStatusBody)
def update_status(todo_id: int, body: TodoUpdateStatusBody):
    todo = TodoTable.get(q.id == todo_id)
    if not todo:
        return fail() 
    todo["completed"] = body.completed
    todo["updated_at"] = now_ts()
    TodoTable.update(todo, q.id == todo_id)
    return ok("Updated", data=todo)  

# ---------- 6. 更新标题 ----------
@app.put("/api/todos/<int:todo_id>/title")
@validate(body=TodoUpdateTitleBody)
def update_title(todo_id: int, body: TodoUpdateTitleBody):
    todo = TodoTable.get(q.id == todo_id)
    if not todo:
        return fail() 
    todo["title"] = body.title
    todo["updated_at"] = now_ts()
    TodoTable.update(todo, q.id == todo_id)
    return ok("Updated", data=todo)  

@app.get("/todoList")
def get_todo_list():
    return send_from_directory(os.path.dirname(__file__), "index.html")

# ---------- 启动 ----------
if __name__ == "__main__":
    if not os.path.exists(DB_FILE):
        db.truncate()
    app.run(debug=True, host='0.0.0.0', port=3000)