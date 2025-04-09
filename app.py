from flask import Flask, render_template, redirect, url_for
import os
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from flask_migrate import Migrate

# إعداد قاعدة البيانات
db = SQLAlchemy()
migrate = Migrate()

# إعداد مدير تسجيل الدخول
login = LoginManager()
login.login_view = 'auth.login'
login.login_message = 'الرجاء تسجيل الدخول للوصول إلى هذه الصفحة.'

def create_app():
    app = Flask(__name__)
    
    # إعدادات التطبيق
    app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'dev-key-for-testing')
    app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DATABASE_URL', 'sqlite:///app.db')
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    
    # تهيئة الإضافات
    db.init_app(app)
    migrate.init_app(app, db)
    login.init_app(app)
    
    # استيراد النماذج
    from models import User
    
    # تسجيل دالة تحميل المستخدم
    @login.user_loader
    def load_user(id):
        return User.query.get(int(id))
    
    # تسجيل البلوبرنتس
    from routes.auth import auth_bp
    from routes.main import main_bp
    from routes.users import users_bp
    from routes.services import services_bp
    from routes.customers import customers_bp
    from routes.sales import sales_bp
    from routes.expenses import expenses_bp
    
    app.register_blueprint(auth_bp)
    app.register_blueprint(main_bp)
    app.register_blueprint(users_bp)
    app.register_blueprint(services_bp)
    app.register_blueprint(customers_bp)
    app.register_blueprint(sales_bp)
    app.register_blueprint(expenses_bp)
    
    # تسجيل مسارات API
    from routes.api import api_bp
    app.register_blueprint(api_bp, url_prefix='/api')
    
    # تسجيل صفحة الخطأ 404
    @app.errorhandler(404)
    def page_not_found(e):
        return render_template('errors/404.html'), 404
    
    # تسجيل صفحة الخطأ 500
    @app.errorhandler(500)
    def internal_server_error(e):
        return render_template('errors/500.html'), 500
    
    # إنشاء جميع الجداول إذا لم تكن موجودة
    with app.app_context():
        db.create_all()
    
    return app
