from flask import Flask, jsonify, request
from flask_pydantic import validate
from pydantic import BaseModel, Field
from tinydb import TinyDB, Query
from datetime import datetime
import os
import bcrypt
from flask_jwt_extended import JWTManager, create_access_token, jwt_required, get_jwt_identity

app = Flask(__name__)
app.config['JWT_SECRET_KEY'] = 'your-secret-key-change-this-in-production'
jwt = JWTManager(app)
CORS = lambda app: app  
from flask_cors import CORS
CORS(app)

# 在JWT配置后添加认证失败回调
@jwt.unauthorized_loader
def custom_unauthorized_response(error_string):
    return jsonify({
        "code": 401,
        "message": "认证失败：请提供有效的Bearer Token"
    }), 401

@jwt.invalid_token_loader
def custom_invalid_token_response(error_string):
    return jsonify({
        "code": 401, 
        "message": "无效的Token格式"
    }), 401

@jwt.expired_token_loader
def custom_expired_token_response(jwt_header, jwt_payload):
    return jsonify({
        "code": 401,
        "message": "Token已过期，请重新登录"
    }), 401

DB_FILE = "database.db"
db = TinyDB(DB_FILE)
TodoTable = db.table("todos")
UserTable = db.table('users')
q = Query()

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

class LoginForm(BaseModel):
    username: str
    password: str
    created_at: int = Field(default_factory=now_ts)

def hash_password(password: str) -> str:
    salt = bcrypt.gensalt()
    return bcrypt.hashpw(password.encode(), salt).decode()

def verify_password(plain_password: str, hashed_password: str) -> bool:
    return bcrypt.checkpw(plain_password.encode(), hashed_password.encode())


@app.post('/register')
def register():
    username = request.json.get('username')
    password = request.json.get('password')
    if not username or not password:
        return fail('用户名或密码不能为空')
    if len(password) < 8:
        return fail('密码长度不能小于8位')

    if UserTable.get(q.username == username):
        return fail('用户名已存在')

    user = {
        'username': username,
        'password_hash': hash_password(password),  # 存储加密后的密码
        'created_at': now_ts()
    }
    UserTable.insert(user)
    access_token = create_access_token(identity=username)
    return ok('注册成功', bearer=access_token)

@app.post('/login')
def login():
    username = request.json.get('username')
    password = request.json.get('password')
    if not username or not password:
        return fail('用户名或密码不能为空')

    user = UserTable.get(q.username == username)
    if not user or not verify_password(password, user['password_hash']):
        return fail('用户名或密码错误', 401)
    
    access_token = create_access_token(identity=username)
    return ok('登录成功', bearer=access_token, username=username)

# ---------- 1. 获取所有待办 ----------
@app.get("/todos")
@jwt_required()
def list_todos():
    todos = TodoTable.all()
    current_user = get_jwt_identity()
    # 过滤出当前用户的待办
    todos = [todo for todo in todos if todo['username'] == current_user]

    return ok("ok", todos_list=todos)

# ---------- 2. 新增一个待办 ----------
@app.post("/todos")
@jwt_required()
def add_todo():
    current_user = get_jwt_identity()
    title = request.json.get("title", "").strip()  
    if not title:
        return fail("title 不能为空")
    todo = {
        "id": next_id(),
        "username": current_user,  
        "title": title,
        "completed": False,
        "created_at": now_ts(),
        "updated_at": now_ts(),
    }
    TodoTable.insert(todo)
    return ok("已新增待办", data=todo)

@app.get("/todos/<int:todo_id>")
@jwt_required()
def get_todo(todo_id: int):
    current_user = get_jwt_identity()
    todo = TodoTable.get((q.id == todo_id) & (q.username == current_user))
    if not todo:
        return fail("Not Found", code=404)
    return ok("ok", data=todo)

@app.delete("/todos/<int:todo_id>")
@jwt_required()
def delete_todo(todo_id: int):
    current_user = get_jwt_identity()
    if not TodoTable.contains((q.id == todo_id) & (q.username == current_user)):
        return fail("Not Found", 404)
    TodoTable.remove((q.id == todo_id) & (q.username == current_user))
    return ok("ok")

@app.put("/todos/<int:todo_id>/status")
@validate(body=TodoUpdateStatusBody)
@jwt_required()
def update_status(todo_id: int, body: TodoUpdateStatusBody):
    current_user = get_jwt_identity()
    todo = TodoTable.get((q.id == todo_id) & (q.username == current_user))
    if not todo:
        return fail("Not Found", 404)
    todo["completed"] = body.completed
    todo["updated_at"] = now_ts()
    TodoTable.update(todo, q.id == todo_id)
    return ok("Updated", data=todo)

@app.put("/todos/<int:todo_id>/title")
@validate(body=TodoUpdateTitleBody)
@jwt_required()
def update_title(todo_id: int, body: TodoUpdateTitleBody):
    current_user = get_jwt_identity()
    todo = TodoTable.get((q.id == todo_id) & (q.username == current_user))
    if not todo:
        return fail("Not Found", 404)
    todo["title"] = body.title
    todo["updated_at"] = now_ts()
    TodoTable.update(todo, q.id == todo_id)
    return ok("Updated", data=todo)  

# ---------- 启动 ----------
if __name__ == "__main__":
    if not os.path.exists(DB_FILE):
        db.truncate()
    app.run(debug=True, host='0.0.0.0', port=3001)  