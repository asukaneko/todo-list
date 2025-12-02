# Flask应用GitHub工作流说明

## 工作流功能

这个GitHub工作流会在以下情况下自动运行：
- 当有Pull Request提交到main或master分支时
- 当修改了Python文件(.py)、requirements.txt或工作流文件时

## 工作流包含的测试步骤

1. **代码检出** - 检出PR中的代码
2. **Python环境设置** - 设置Python 3.9环境
3. **依赖安装** - 安装requirements.txt中的所有依赖包
4. **Python语法检查** - 检查Flask应用的Python语法
5. **Flask应用功能测试** - 运行完整的Flask应用测试，包括：
   - 应用启动测试
   - API端点测试
   - 待办事项CRUD操作测试
6. **依赖包验证** - 验证requirements.txt格式正确
7. **代码风格检查** - 使用flake8检查代码风格
8. **测试结果上传** - 上传测试结果作为artifact

## 测试覆盖的功能

- ✅ Flask应用启动
- ✅ 根路径访问
- ✅ 获取所有待办事项
- ✅ 添加新待办事项
- ✅ 获取单个待办事项
- ✅ 更新待办事项状态
- ✅ 删除待办事项

## 文件说明

- `.github/workflows/test-flask-pr.yml` - GitHub工作流配置文件
- `test_flask_app.py` - Flask应用测试脚本
- `requirements.txt` - Python依赖包列表

## 如何查看测试结果

1. 在GitHub仓库中，进入"Actions"标签页
2. 选择对应的PR工作流运行记录
3. 查看详细的测试日志和结果
4. 如果测试失败，可以下载测试结果artifact进行分析

## 自定义配置

如果需要修改工作流配置，可以编辑`.github/workflows/test-flask-pr.yml`文件：

- 修改触发条件：调整`on.pull_request`配置
- 修改Python版本：调整`python-version`参数
- 添加更多测试步骤：在`steps`部分添加新的测试任务

## 注意事项

- 确保所有Python文件语法正确
- 保持requirements.txt文件格式正确
- 测试使用临时数据库文件，不会影响生产数据