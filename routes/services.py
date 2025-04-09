from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_required, current_user
from models import Service, ServiceProvider
from app import db

services_bp = Blueprint('services', __name__, url_prefix='/services')

@services_bp.route('/')
@login_required
def index():
    services = Service.query.all()
    return render_template('services.html', services=services)

@services_bp.route('/add', methods=['GET', 'POST'])
@login_required
def add():
    if request.method == 'POST':
        service = Service(
            name=request.form['name'],
            description=request.form.get('description', ''),
            service_code=request.form['service_code'],
            service_type=request.form['service_type'],
            duration=int(request.form.get('duration', 60)),
            price=float(request.form['price']),
            category=request.form['category'],
            is_active=True if request.form.get('is_active') else False
        )
        
        db.session.add(service)
        db.session.commit()
        
        flash('تم إضافة الخدمة بنجاح', 'success')
        return redirect(url_for('services.index'))
    
    return render_template('services/add.html')

@services_bp.route('/edit/<int:id>', methods=['GET', 'POST'])
@login_required
def edit(id):
    service = Service.query.get_or_404(id)
    
    if request.method == 'POST':
        service.name = request.form['name']
        service.description = request.form.get('description', '')
        service.service_code = request.form['service_code']
        service.service_type = request.form['service_type']
        service.duration = int(request.form.get('duration', 60))
        service.price = float(request.form['price'])
        service.category = request.form['category']
        service.is_active = True if request.form.get('is_active') else False
        
        db.session.commit()
        
        flash('تم تحديث الخدمة بنجاح', 'success')
        return redirect(url_for('services.index'))
    
    return render_template('services/edit.html', service=service)

@services_bp.route('/delete/<int:id>', methods=['POST'])
@login_required
def delete(id):
    service = Service.query.get_or_404(id)
    
    # التحقق من عدم وجود مبيعات مرتبطة بالخدمة
    if service.sale_items.count() > 0:
        flash('لا يمكن حذف الخدمة لأنها مرتبطة بعمليات بيع', 'danger')
        return redirect(url_for('services.index'))
    
    db.session.delete(service)
    db.session.commit()
    
    flash('تم حذف الخدمة بنجاح', 'success')
    return redirect(url_for('services.index'))

@services_bp.route('/view/<int:id>')
@login_required
def view(id):
    service = Service.query.get_or_404(id)
    return render_template('services/view.html', service=service)

@services_bp.route('/providers')
@login_required
def providers():
    providers = ServiceProvider.query.all()
    return render_template('services/providers.html', providers=providers)

@services_bp.route('/providers/add', methods=['GET', 'POST'])
@login_required
def add_provider():
    if request.method == 'POST':
        provider = ServiceProvider(
            name=request.form['name'],
            specialization=request.form['specialization'],
            phone=request.form['phone'],
            email=request.form.get('email', ''),
            is_active=True if request.form.get('is_active') else False
        )
        
        db.session.add(provider)
        db.session.commit()
        
        flash('تم إضافة مقدم الخدمة بنجاح', 'success')
        return redirect(url_for('services.providers'))
    
    return render_template('services/add_provider.html')

@services_bp.route('/providers/edit/<int:id>', methods=['GET', 'POST'])
@login_required
def edit_provider(id):
    provider = ServiceProvider.query.get_or_404(id)
    
    if request.method == 'POST':
        provider.name = request.form['name']
        provider.specialization = request.form['specialization']
        provider.phone = request.form['phone']
        provider.email = request.form.get('email', '')
        provider.is_active = True if request.form.get('is_active') else False
        
        db.session.commit()
        
        flash('تم تحديث بيانات مقدم الخدمة بنجاح', 'success')
        return redirect(url_for('services.providers'))
    
    return render_template('services/edit_provider.html', provider=provider)

@services_bp.route('/providers/delete/<int:id>', methods=['POST'])
@login_required
def delete_provider(id):
    provider = ServiceProvider.query.get_or_404(id)
    
    # التحقق من عدم وجود خدمات مرتبطة بمقدم الخدمة
    if provider.provided_services.count() > 0:
        flash('لا يمكن حذف مقدم الخدمة لأنه مرتبط بخدمات', 'danger')
        return redirect(url_for('services.providers'))
    
    db.session.delete(provider)
    db.session.commit()
    
    flash('تم حذف مقدم الخدمة بنجاح', 'success')
    return redirect(url_for('services.providers'))
