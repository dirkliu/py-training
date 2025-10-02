from datetime import datetime, timedelta
import threading
import time
from flask import Flask, render_template, redirect, url_for, request, flash, jsonify
from flask_login import LoginManager, login_user, login_required, logout_user, current_user
from werkzeug.security import generate_password_hash
from models import db, User, UserLog
from config import Config

# 创建Flask应用
app = Flask(__name__, template_folder='../frontend/templates', static_folder='../frontend/static')
app.config.from_object(Config)

# 初始化数据库
db.init_app(app)

# 初始化登录管理器
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

# 加载用户
@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

# 初始化数据库
def init_db():
    with app.app_context():
        db.create_all()
        # 检查是否已有管理员用户，如果没有则创建一个
        admin = User.query.filter_by(username='admin').first()
        if not admin:
            admin = User(username='admin')
            admin.set_password('admin123')  # 初始密码
            db.session.add(admin)
            db.session.commit()

# 定时任务：检查用户登录超时
def check_login_time():
    while True:
        with app.app_context():
            # 获取当前时间
            now = datetime.utcnow()
            # 查询所有登录状态为True的用户
            logged_in_users = User.query.filter_by(is_logged_in=True).all()
            
            for user in logged_in_users:
                # 检查登录时间是否超过设定的自动下线时间
                if user.login_time and now - user.login_time > timedelta(seconds=Config.AUTO_LOGOUT_TIME):
                    # 更新用户状态为下线
                    user.is_logged_in = False
                    # 更新最近的日志记录，设置下线时间
                    latest_log = UserLog.query.filter_by(user_id=user.id, logout_time=None).order_by(UserLog.login_time.desc()).first()
                    if latest_log:
                        latest_log.logout_time = now
                    # 提交更改
                    db.session.commit()
        # 等待设定的轮询间隔后再次执行
        time.sleep(Config.POLLING_INTERVAL)

# 登录路由
@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('dashboard'))
    
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        user = User.query.filter_by(username=username).first()
        
        if user and user.check_password(password):
            # 获取用户IP
            user_ip = request.remote_addr
            # 更新用户信息
            user.last_login_ip = user_ip
            user.is_logged_in = True
            user.login_time = datetime.utcnow()
            # 创建登录日志
            user_log = UserLog(
                user_id=user.id,
                username=user.username,
                login_ip=user_ip,
                login_time=datetime.utcnow()
            )
            # 添加到数据库
            db.session.add(user_log)
            db.session.commit()
            # 登录用户
            login_user(user)
            return redirect(url_for('dashboard'))
        else:
            flash('用户名或密码错误')
    
    return render_template('login.html')

# 退出登录路由
@app.route('/logout')
@login_required
def logout():
    # 更新用户状态
    user = current_user._get_current_object()
    user.is_logged_in = False
    # 更新最近的日志记录，设置下线时间
    latest_log = UserLog.query.filter_by(user_id=user.id, logout_time=None).order_by(UserLog.login_time.desc()).first()
    if latest_log:
        latest_log.logout_time = datetime.utcnow()
    # 提交更改
    db.session.commit()
    # 退出登录
    logout_user()
    return redirect(url_for('login'))

# 仪表盘路由
@app.route('/')
@login_required
def dashboard():
    return render_template('dashboard.html')

# 用户信息管理路由
@app.route('/users', methods=['GET'])
@login_required
def users():
    # 获取所有用户
    all_users = User.query.all()
    return render_template('users.html', users=all_users)

# 重置密码路由
@app.route('/reset_password/<int:user_id>', methods=['POST'])
@login_required
def reset_password(user_id):
    # 获取新密码
    new_password = request.form['new_password']
    # 查找用户
    user = User.query.get(user_id)
    if user:
        # 设置新密码
        user.set_password(new_password)
        db.session.commit()
        flash(f'用户 {user.username} 的密码已重置')
    else:
        flash('用户不存在')
    return redirect(url_for('users'))

# 用户日志看板路由
@app.route('/logs', methods=['GET'])
@login_required
def logs():
    # 获取所有用户日志
    all_logs = UserLog.query.order_by(UserLog.login_time.desc()).all()
    return render_template('logs.html', logs=all_logs)

# API: 获取当前登录用户信息
@app.route('/api/user_info', methods=['GET'])
@login_required
def user_info():
    user = current_user._get_current_object()
    return jsonify({
        'username': user.username,
        'last_login_ip': user.last_login_ip,
        'is_logged_in': user.is_logged_in,
        'login_time': user.login_time.isoformat() if user.login_time else None
    })

# API: 检查登录状态
@app.route('/api/check_login', methods=['GET'])
def check_login():
    return jsonify({
        'is_logged_in': current_user.is_authenticated
    })

# 启动定时任务
threading.Thread(target=check_login_time, daemon=True).start()

if __name__ == '__main__':
    # 初始化数据库
    init_db()
    # 启动应用
    app.run(debug=True, host='0.0.0.0', port=5000)