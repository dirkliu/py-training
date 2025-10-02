from datetime import datetime
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash

# 创建数据库对象
db = SQLAlchemy()

class User(db.Model):
    __tablename__ = 'users'
    
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password_hash = db.Column(db.String(200), nullable=False)
    last_login_ip = db.Column(db.String(50))
    is_logged_in = db.Column(db.Boolean, default=False)
    login_time = db.Column(db.DateTime)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    is_active = db.Column(db.Boolean, default=True)  # Flask-Login所需
    
    # 设置密码（加密）
    def set_password(self, password):
        self.password_hash = generate_password_hash(password)
    
    # 验证密码
    def check_password(self, password):
        return check_password_hash(self.password_hash, password)
    
    # Flask-Login 所需的方法
    @property
    def is_authenticated(self):
        return True
    
    @property
    def is_anonymous(self):
        return False
    
    def get_id(self):
        return str(self.id)

class UserLog(db.Model):
    __tablename__ = 'user_logs'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    username = db.Column(db.String(80), nullable=False)
    login_ip = db.Column(db.String(50), nullable=False)
    login_time = db.Column(db.DateTime, nullable=False)
    logout_time = db.Column(db.DateTime)
    
    # 建立与用户的关系
    user = db.relationship('User', backref=db.backref('logs', lazy=True))