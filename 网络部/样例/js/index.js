// index.js
import express from 'express';
import multer from 'multer';
import { Low } from 'lowdb';
import { JSONFile } from 'lowdb/node';
import Joi from 'joi';
import cors from 'cors';
import { fileURLToPath } from 'url';
import { dirname, join } from 'path';

const __dirname = dirname(fileURLToPath(import.meta.url));

// 初始化 DB
// 修改数据库初始化部分
const adapter = new JSONFile(join(__dirname, 'db2.json'));
const db = new Low(adapter, { todos: [] }); // 添加默认数据结构
await db.read();
// 删除原来的 db.data ||= { todos: [] } 和 await db.write()
db.data ||= { todos: [] };
await db.write();

const app = express();
app.use(cors({
  origin: '*' // 允许所有来源
}));         
app.use(express.json());   // 用于 PUT  JSON 解析

// 工具
const nextId = () => Math.max(0, ...db.data.todos.map(t => t.id)) + 1;
const now   = () => Math.floor(Date.now() / 1000);

const ok = (res, message = 'ok', extra = {}) =>
  res.json({ code: 200, message, ...extra });
const fail = (res, message = 'Invalid input', code = 400) =>
  res.status(code).json({ code, message });

// ---------- 1. 获取所有待办 ----------
app.get('/todos', async (_req, res) => {
  await db.read();
  ok(res, 'ok', { todos_list: db.data.todos });
});

// ---------- 2. 新增待办（multipart/form-data） ----------
const upload = multer(); // 默认存在内存
const addSchema = Joi.object({ title: Joi.string().trim().required() });
app.post('/todos', upload.none(), async (req, res) => {
  const { error, value } = addSchema.validate(req.body);
  if (error) return fail(res, 'title 不能为空');
  const todo = {
    id: nextId(),
    title: value.title,
    completed: false,
    created_at: now(),
    updated_at: now(),
  };
  db.data.todos.push(todo);
  await db.write();
  ok(res, '创建成功', { data: todo });
});

// ---------- 3. 获取单个待办 ----------
app.get('/todos/:id', async (req, res) => {
  await db.read();
  const id = Number(req.params.id);
  const todo = db.data.todos.find(t => t.id === id);
  if (!todo) return fail(res, 'Not Found', 404);
  ok(res, 'ok', { data: todo });
});

// ---------- 4. 删除指定待办 ----------
app.delete('/todos/:id', async (req, res) => {
  await db.read();
  const id = Number(req.params.id);
  const idx = db.data.todos.findIndex(t => t.id === id);
  if (idx === -1) return fail(res, 'Invalid input');
  db.data.todos.splice(idx, 1);
  await db.write();
  ok(res, 'ok');
});

// ---------- 5. 更新完成状态 ----------
const statusSchema = Joi.object({ completed: Joi.boolean().required() });
app.put('/todos/:id/status', async (req, res) => {
  const { error, value } = statusSchema.validate(req.body);
  if (error) return fail(res, error.details[0].message);
  await db.read();
  const id = Number(req.params.id);
  const todo = db.data.todos.find(t => t.id === id);
  if (!todo) return fail(res, 'Invalid input');
  todo.completed = value.completed;
  todo.updated_at = now();
  await db.write();
  ok(res, '更新成功', { data: todo });
});

// ---------- 6. 更新标题 ----------
const titleSchema = Joi.object({ title: Joi.string().trim().required() });
app.put('/todos/:id/title', async (req, res) => {
  const { error, value } = titleSchema.validate(req.body);
  if (error) return fail(res, error.details[0].message);
  await db.read();
  const id = Number(req.params.id);
  const todo = db.data.todos.find(t => t.id === id);
  if (!todo) return fail(res, 'Invalid input');
  todo.title = value.title;
  todo.updated_at = now();
  await db.write();
  ok(res, '更新成功', { data: todo });
});

// ---------- 启动 ----------
const PORT = process.env.PORT || 3000;
app.listen(PORT, () => console.log(`Todo API on http://localhost:${PORT}`));