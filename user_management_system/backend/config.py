import os

class Config:
    # 密钥，用于保护表单数据和会话
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'hard-to-guess-string'
    
    # 数据库配置
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or 'sqlite:///users.db'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    # 自动下线时间（秒）
    AUTO_LOGOUT_TIME = 180  # 3分钟 = 180秒
    
    # 轮询间隔（秒）
    POLLING_INTERVAL = 120  # 2分钟 = 120秒