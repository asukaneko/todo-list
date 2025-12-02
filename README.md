# Todo API 项目

一个完整的待办事项管理系统，包含Flask后端API和Express.js后端API，支持完整的CRUD操作。

## 项目概述

本项目提供了两种后端实现：
1. **Flask版本**：使用Python Flask框架，包含数据验证、数据库操作和完整的RESTful API
2. **Express.js版本**：使用Node.js Express框架，提供相同的API功能

## 功能特性

### 核心功能
- ✅ 创建、读取、更新、删除待办事项
- ✅ 待办事项状态管理（完成/未完成）
- ✅ 数据验证和错误处理
- ✅ CORS跨域支持
- ✅ 数据库持久化存储

### Flask版本特性
- 使用Flask 2.3.3 + Flask-Pydantic进行数据验证
- TinyDB轻量级JSON数据库
- Pydantic模型验证请求和响应数据
- 完整的RESTful API设计

### Express.js版本特性
- Express.js + LowDB数据库
- Joi数据验证
- Multer处理表单数据
- 异步数据库操作

## 项目结构

```
todo/
├── .github/workflows/          # GitHub Actions工作流
│   └── test-flask-pr.yml      # PR测试工作流
├── 网络部/样例/python/        # Flask版本
│   ├── app.py                # Flask主应用
│   └──app_login.py          # 登录功能示例
├── 研发部/样例/dist/         # 前端文件
│   ├── CSS/                 # 样式文件
│   └── JS/                  # JavaScript文件
├── requirements.txt         # Python依赖
├── test_flask_app.py        # Flask应用测试脚本
├── GITHUB_WORKFLOW_README.md # 工作流说明
└── README.md               # 本文件
```

## 快速开始

### Flask版本

1. **安装依赖**
   ```bash
   pip install -r requirements.txt
   ```

2. **启动应用**
   ```bash
   cd 网络部/样例/python
   python app.py
   ```

3. **访问应用**
   - API地址：http://localhost:3000
   - API文档：见下方API接口说明

### Express.js版本

1. **安装依赖**
   ```bash
   npm install express multer lowdb joi cors
   ```

2. **启动应用**
   ```bash
   node index.js
   ```

3. **访问应用**
   - API地址：http://localhost:3000

## API接口文档

### Flask版本 API

#### 1. 获取所有待办事项
```http
GET /api/todos
```

**响应示例**
```json
{
  "code": 200,
  "message": "ok",
  "todos_list": [
    {
      "id": 1,
      "title": "学习Flask",
      "completed": false,
      "created_at": 1634567890,
      "updated_at": 1634567890
    }
  ]
}
```

#### 2. 创建待办事项
```http
POST /api/todos
Content-Type: application/json

{
  "title": "新的待办事项"
}
```

**响应示例**
```json
{
  "code": 200,
  "message": "Created",
  "data": {
    "id": 2,
    "title": "新的待办事项",
    "completed": false,
    "created_at": 1634567890,
    "updated_at": 1634567890
  }
}
```

#### 3. 获取单个待办事项
```http
GET /api/todos/{id}
```

#### 4. 更新待办事项状态
```http
PUT /api/todos/{id}/status
Content-Type: application/json

{
  "completed": true
}
```

#### 5. 更新待办事项标题
```http
PUT /api/todos/{id}/title
Content-Type: application/json

{
  "title": "更新后的标题"
}
```

#### 6. 删除待办事项
```http
DELETE /api/todos/{id}
```

### Express.js版本 API

Express.js版本提供相同的API端点，但路径略有不同：
- `GET /todos` - 获取所有待办
- `POST /todos` - 创建待办（支持multipart/form-data）
- `GET /todos/:id` - 获取单个待办
- `PUT /todos/:id/status` - 更新状态
- `PUT /todos/:id/title` - 更新标题
- `DELETE /todos/:id` - 删除待办

## 数据库

### Flask版本
- 使用TinyDB作为JSON数据库
- 数据库文件：`db.json`
- 自动生成ID，支持数据持久化

### Express.js版本
- 使用LowDB作为JSON数据库
- 数据库文件：`db2.json`
- 异步读写操作

## 测试

### 手动测试
```bash
# 运行Flask应用测试
python test_flask_app.py
```

### 自动化测试（GitHub Actions）
项目配置了GitHub Actions工作流，在以下情况下自动运行测试：
- 创建Pull Request时
- 推送到主分支时

测试包括：
1. 代码语法检查
2. 依赖验证
3. Flask应用功能测试
4. API端点测试

## 部署

### 本地部署
```bash
# Flask版本
python app.py

# Express.js版本
node index.js
```

### 生产环境建议
1. 使用Gunicorn或uWSGI部署Flask应用
2. 使用PM2管理Node.js进程
3. 配置Nginx反向代理
4. 使用环境变量管理配置

## 开发指南

### 代码规范
- Python代码遵循PEP8规范
- JavaScript代码使用ES6+语法
- API响应统一格式：`{"code": 200, "message": "ok", ...}`

### 添加新功能
1. 在`app.py`中添加新的路由和业务逻辑
2. 在`test_flask_app.py`中添加对应的测试用例
3. 更新API文档

## 故障排除

### 常见问题

1. **数据库文件不存在**
   - Flask版本会自动创建`db.json`
   - Express.js版本会自动创建`db2.json`

2. **端口被占用**
   - 修改`app.py`中的端口号（默认3000）
   - 修改`index.js`中的`PORT`环境变量

3. **依赖安装失败**
   - 确保使用正确的Python版本（3.7+）
   - 使用虚拟环境：`python -m venv venv`

### 日志查看
- Flask应用在控制台输出访问日志
- 错误信息会返回给客户端

## 贡献指南

1. Fork本仓库
2. 创建功能分支：`git checkout -b feature/新功能`
3. 提交更改：`git commit -m '添加新功能'`
4. 推送到分支：`git push origin feature/新功能`
5. 创建Pull Request

## 许可证

本项目采用MIT许可证。详见LICENSE文件。

## 联系方式

如有问题或建议，请通过以下方式联系：
- 提交GitHub Issue
- 查看项目文档

---

**最后更新**：2024年
**版本**：1.0.0