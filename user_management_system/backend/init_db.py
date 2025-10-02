#!/usr/bin/env python
"""
数据库初始化脚本
用于确保数据库表被正确创建
"""

import os
import sys
from app import app
from models import db, User
from datetime import datetime

if __name__ == '__main__':
    # 确保在应用上下文中初始化数据库
    with app.app_context():
        print("正在创建数据库表...")
        # 强制创建所有表
        db.create_all()
        print("数据库表创建完成")
        
        # 检查是否已有管理员用户
        admin = User.query.filter_by(username='admin').first()
        if not admin:
            print("正在创建管理员用户...")
            admin = User(
                username='admin',
                created_at=datetime.utcnow()
            )
            admin.set_password('admin123')  # 初始密码
            db.session.add(admin)
            db.session.commit()
            print("管理员用户创建完成")
        else:
            print("管理员用户已存在")
            
        print("\n数据库初始化成功！")
        print("默认管理员账号: admin")
        print("默认管理员密码: admin123")
        print("请登录后修改默认密码以保证安全")