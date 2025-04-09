from flask import Blueprint, jsonify, request
from models import User
from app import db
from flask_login import current_user, login_required

users_bp = Blueprint('users', __name__, url_prefix='/users')

@users_bp.route('/')
@login_required
def index():
    if not current_user.is_admin:
        return redirect(url_for('main.dashboard'))
    
    users = User.query.all()
    return render_template('users/index.html', users=users)

@users_bp.route('/profile')
@login_required
def profile():
    return render_template('users/profile.html')

@users_bp.route('/profile/update', methods=['POST'])
@login_required
def update_profile():
    if request.method == 'POST':
        user = current_user
        
        user.full_name = request.form['full_name']
        user.email = request.form['email']
        user.phone = request.form['phone']
        
        db.session.commit()
        flash('تم تحديث الملف الشخصي بنجاح', 'success')
        
        return redirect(url_for('users.profile'))
    
    return redirect(url_for('users.profile'))

@users_bp.route('/change-password', methods=['GET', 'POST'])
@login_required
def change_password():
    if request.method == 'POST':
        current_password = request.form['current_password']
        new_password = request.form['new_password']
        confirm_password = request.form['confirm_password']
        
        if not current_user.check_password(current_password):
            flash('كلمة المرور الحالية غير صحيحة', 'danger')
            return redirect(url_for('users.change_password'))
        
        if new_password != confirm_password:
            flash('كلمات المرور الجديدة غير متطابقة', 'danger')
            return redirect(url_for('users.change_password'))
        
        current_user.set_password(new_password)
        db.session.commit()
        
        flash('تم تغيير كلمة المرور بنجاح', 'success')
        return redirect(url_for('users.profile'))
    
    return render_template('users/change_password.html')
