#!/usr/bin/env python3
"""
Flask应用测试脚本
用于在GitHub Actions中测试Flask应用功能
"""

import sys
import os
import tempfile
import json
from pathlib import Path

# 添加Flask应用路径到系统路径
app_path = Path(__file__).parent / "网络部" / "样例" / "python"
sys.path.append(str(app_path))

def test_flask_app():
    """测试Flask应用的基本功能"""
    try:
        # 导入Flask应用
        from app import app, TodoTable, q
        
        # 创建临时数据库文件
        with tempfile.NamedTemporaryFile(suffix='.json', delete=False) as temp_db:
            temp_db_path = temp_db.name
        
        # 设置临时数据库路径
        import app as flask_app_module
        flask_app_module.DB_FILE = temp_db_path
        
        # 重新初始化数据库
        from tinydb import TinyDB
        flask_app_module.db = TinyDB(temp_db_path)
        flask_app_module.TodoTable = flask_app_module.db.table("todos")
        flask_app_module.q = Query()
        
        print("🔧 使用临时数据库文件:", temp_db_path)
        
        # 测试应用是否能正常启动
        with app.test_client() as client:
            print("✅ Flask应用启动成功")
            
            # 测试1: 根路径访问
            print("\n📋 测试1: 根路径访问")
            response = client.get('/')
            print(f"   状态码: {response.status_code}")
            assert response.status_code in [200, 404], f"根路径返回状态码: {response.status_code}"
            print("   ✅ 根路径访问测试通过")
            
            # 测试2: 获取待办事项列表
            print("\n📋 测试2: 获取待办事项列表")
            response = client.get('/api/todos')
            print(f"   状态码: {response.status_code}")
            assert response.status_code == 200, f"API端点返回状态码: {response.status_code}"
            
            data = response.get_json()
            assert data['code'] == 200, f"响应代码: {data['code']}"
            print("   ✅ 获取待办事项列表测试通过")
            
            # 测试3: 添加待办事项
            print("\n📋 测试3: 添加待办事项")
            test_todo = {'title': 'GitHub Actions测试待办事项'}
            response = client.post('/api/todos', 
                                 json=test_todo,
                                 content_type='application/json')
            print(f"   状态码: {response.status_code}")
            assert response.status_code == 200, f"添加待办事项返回状态码: {response.status_code}"
            
            data = response.get_json()
            assert data['code'] == 200, f"响应代码: {data['code']}"
            assert 'data' in data, "响应中缺少data字段"
            assert data['data']['title'] == test_todo['title'], "待办事项标题不匹配"
            print("   ✅ 添加待办事项测试通过")
            
            # 测试4: 获取单个待办事项
            print("\n📋 测试4: 获取单个待办事项")
            todo_id = data['data']['id']
            response = client.get(f'/api/todos/{todo_id}')
            print(f"   状态码: {response.status_code}")
            assert response.status_code == 200, f"获取单个待办事项返回状态码: {response.status_code}"
            
            data = response.get_json()
            assert data['code'] == 200, f"响应代码: {data['code']}"
            print("   ✅ 获取单个待办事项测试通过")
            
            # 测试5: 更新待办事项状态
            print("\n📋 测试5: 更新待办事项状态")
            response = client.put(f'/api/todos/{todo_id}/status',
                                json={'completed': True},
                                content_type='application/json')
            print(f"   状态码: {response.status_code}")
            assert response.status_code == 200, f"更新状态返回状态码: {response.status_code}"
            
            data = response.get_json()
            assert data['code'] == 200, f"响应代码: {data['code']}"
            print("   ✅ 更新待办事项状态测试通过")
            
            # 测试6: 删除待办事项
            print("\n📋 测试6: 删除待办事项")
            response = client.delete(f'/api/todos/{todo_id}')
            print(f"   状态码: {response.status_code}")
            assert response.status_code == 200, f"删除待办事项返回状态码: {response.status_code}"
            
            data = response.get_json()
            assert data['code'] == 200, f"响应代码: {data['code']}"
            print("   ✅ 删除待办事项测试通过")
            
            # 清理临时文件
            if os.path.exists(temp_db_path):
                os.unlink(temp_db_path)
            
            print("\n🎉 所有测试通过！Flask应用功能正常")
            return True
            
    except Exception as e:
        print(f"\n❌ 测试失败: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_flask_app()
    sys.exit(0 if success else 1)