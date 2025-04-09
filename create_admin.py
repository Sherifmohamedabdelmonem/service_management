#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
سكريبت إنشاء مستخدم مسؤول للنظام
يستخدم هذا السكريبت لإنشاء مستخدم مسؤول أولي للنظام
"""

from app import create_app, db
from models import User

def create_admin():
    """إنشاء مستخدم مسؤول جديد"""
    app = create_app()
    
    with app.app_context():
        # التحقق من وجود مستخدمين
        if User.query.count() > 0:
            print("يوجد مستخدمين بالفعل في النظام. لا يمكن إنشاء مستخدم مسؤول جديد.")
            return
        
        # إنشاء مستخدم مسؤول جديد
        admin = User(
            username='admin',
            email='admin@example.com',
            full_name='مدير النظام',
            is_admin=True
        )
        admin.set_password('admin123')
        
        db.session.add(admin)
        db.session.commit()
        
        print("تم إنشاء مستخدم مسؤول بنجاح!")
        print("اسم المستخدم: admin")
        print("كلمة المرور: admin123")
        print("يرجى تغيير كلمة المرور بعد تسجيل الدخول لأول مرة.")

if __name__ == '__main__':
    create_admin()
