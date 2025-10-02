#!/usr/bin/env python
"""
数据库表结构更新脚本
用于添加is_active列到users表
"""

import os
import sys
from app import app
from models import db

if __name__ == '__main__':
    with app.app_context():
        print("正在更新数据库表结构...")
        
        # 获取数据库连接
        conn = db.engine.connect()
        
        try:
            # 检查is_active列是否已存在
            result = conn.execute(db.text("PRAGMA table_info(users)"))
            columns = [column[1] for column in result.fetchall()]
            
            if 'is_active' not in columns:
                # 添加is_active列
                conn.execute(db.text("ALTER TABLE users ADD COLUMN is_active BOOLEAN DEFAULT TRUE"))
                print("已成功添加is_active列到users表")
            else:
                print("is_active列已存在，无需添加")
            
            # 提交事务
            conn.commit()
            print("数据库表结构更新完成")
        except Exception as e:
            print(f"更新数据库表结构时出错: {e}")
        finally:
            conn.close()