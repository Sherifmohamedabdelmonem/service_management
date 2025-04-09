from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_user, logout_user, login_required, current_user
from urllib.parse import urlparse
from app import db
from models import User
from werkzeug.security import generate_password_hash

auth_bp = Blueprint('auth', __name__, url_prefix='/auth')

@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('main.dashboard'))
    
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        remember_me = 'remember_me' in request.form
        
        user = User.query.filter_by(username=username).first()
        
        if user is None or not user.check_password(password):
            flash('اسم المستخدم أو كلمة المرور غير صحيحة', 'danger')
            return redirect(url_for('auth.login'))
        
        login_user(user, remember=remember_me)
        
        next_page = request.args.get('next')
        if not next_page or urlparse(next_page).netloc != '':
            next_page = url_for('main.dashboard')
        
        return redirect(next_page)
    
    return render_template('auth/login.html')

@auth_bp.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('auth.login'))

@auth_bp.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('main.dashboard'))
    
    if request.method == 'POST':
        username = request.form['username']
        email = request.form['email']
        password = request.form['password']
        confirm_password = request.form['confirm_password']
        full_name = request.form['full_name']
        phone = request.form['phone']
        
        if password != confirm_password:
            flash('كلمات المرور غير متطابقة', 'danger')
            return redirect(url_for('auth.register'))
        
        if User.query.filter_by(username=username).first():
            flash('اسم المستخدم مستخدم بالفعل', 'danger')
            return redirect(url_for('auth.register'))
        
        if User.query.filter_by(email=email).first():
            flash('البريد الإلكتروني مستخدم بالفعل', 'danger')
            return redirect(url_for('auth.register'))
        
        user = User(
            username=username,
            email=email,
            full_name=full_name,
            phone=phone
        )
        user.set_password(password)
        
        # جعل أول مستخدم مسؤولًا
        if User.query.count() == 0:
            user.is_admin = True
        
        db.session.add(user)
        db.session.commit()
        
        flash('تم إنشاء الحساب بنجاح، يمكنك الآن تسجيل الدخول', 'success')
        return redirect(url_for('auth.login'))
    
    return render_template('auth/register.html')
