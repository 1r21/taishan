#!/usr/bin/env python
"""
测试婚礼留言API的脚本
Script to test the wedding message API (from wedding_wishes.py)
"""
import os
import sys
import json

# Add parent directory to path to import app modules
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Import requests for API testing
try:
    import requests
except ImportError:
    print("请先安装requests: pip install requests")
    sys.exit(1)

# Import port from settings
from app.setting import PORT

# API 基础URL - 使用settings.py中定义的端口 (PORT=8081)
BASE_URL = f"http://localhost:{PORT}/api"

def add_test_message():
    """添加测试留言 / Add a test message"""
    print("\n添加测试留言...")
    url = f"{BASE_URL}/wedding/save_message"
    data = {
        "name": "测试用户",
        "message": "祝福你们新婚快乐，白头偕老！",
        "phone": "13800138000",
        "attending": True,
        "guests": 2
    }
    
    try:
        response = requests.post(url, json=data)
        if response.status_code == 200:
            result = response.json()
            if result["code"] == 0:
                print("✅ 留言添加成功!")
                print(f"留言ID: {result['data']['id']}")
                return result['data']['id']
            else:
                print(f"❌ 留言添加失败: {result['message']}")
        else:
            print(f"❌ 请求失败，状态码: {response.status_code}")
    except Exception as e:
        print(f"❌ 发生错误: {e}")
    
    return None

def get_all_messages():
    """获取所有留言 / Get all messages"""
    print("\n获取所有留言...")
    url = f"{BASE_URL}/wedding/messages"
    
    try:
        response = requests.get(url)
        if response.status_code == 200:
            result = response.json()
            if result["code"] == 0:
                messages = result['data']['list']
                total = result['data']['total']
                print(f"✅ 成功获取 {len(messages)} 条留言 (总计: {total})")
                
                if messages:
                    print("\n最新留言:")
                    latest = messages[0]
                    print(f"姓名: {latest['name']}")
                    print(f"留言: {latest['message']}")
                    print(f"时间: {latest['created_at']}")
                return True
            else:
                print(f"❌ 获取留言失败: {result['message']}")
        else:
            print(f"❌ 请求失败，状态码: {response.status_code}")
    except Exception as e:
        print(f"❌ 发生错误: {e}")
    
    return False

def get_message_by_id(message_id):
    """根据ID获取留言 / Get message by ID"""
    print(f"\n获取ID为 {message_id} 的留言...")
    url = f"{BASE_URL}/wedding/message"
    
    try:
        response = requests.post(url, json={"id": message_id})
        if response.status_code == 200:
            result = response.json()
            if result["code"] == 0:
                message = result['data']
                print("✅ 成功获取指定留言!")
                print(f"姓名: {message['name']}")
                print(f"留言: {message['message']}")
                print(f"参加婚礼: {'是' if message['attending'] else '否'}")
                print(f"随行人数: {message['guests']}")
                print(f"时间: {message['created_at']}")
                return True
            else:
                print(f"❌ 获取留言失败: {result['message']}")
        else:
            print(f"❌ 请求失败，状态码: {response.status_code}")
    except Exception as e:
        print(f"❌ 发生错误: {e}")
    
    return False

def run_tests():
    """运行所有测试 / Run all tests"""
    print(f"===== 婚礼留言API测试 (PORT: {PORT}) =====")
    
    # 测试添加留言
    message_id = add_test_message()
    if not message_id:
        print("❌ 添加留言测试失败，无法继续测试")
        return False
    
    # 测试获取所有留言
    if not get_all_messages():
        print("❌ 获取所有留言测试失败")
    
    # 测试根据ID获取留言
    if not get_message_by_id(message_id):
        print("❌ 根据ID获取留言测试失败")
    
    print("\n✅ 所有测试完成")
    return True

if __name__ == "__main__":
    run_tests() 