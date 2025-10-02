#!/usr/bin/env python
"""
用户管理系统启动脚本
"""

import os
import sys
from app import app, init_db

if __name__ == '__main__':
    # 确保在应用上下文中初始化数据库
    with app.app_context():
        print("正在初始化数据库...")
        init_db()
        print("数据库初始化完成")
    
    # 启动应用
    print("正在启动用户管理系统...")
    print("访问 http://localhost:5000 进入系统")
    print("默认管理员账号: admin")
    print("默认管理员密码: admin123")
    print("请登录后修改默认密码以保证安全")
    
    app.run(debug=True, host='0.0.0.0', port=5000)