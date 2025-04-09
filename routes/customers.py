from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_required, current_user
from models import Customer
from app import db

customers_bp = Blueprint('customers', __name__, url_prefix='/customers')

@customers_bp.route('/')
@login_required
def index():
    customers = Customer.query.all()
    return render_template('customers.html', customers=customers)

@customers_bp.route('/add', methods=['GET', 'POST'])
@login_required
def add():
    if request.method == 'POST':
        customer = Customer(
            name=request.form['name'],
            phone=request.form['phone'],
            email=request.form.get('email', ''),
            address=request.form.get('address', '')
        )
        
        db.session.add(customer)
        db.session.commit()
        
        flash('تم إضافة العميل بنجاح', 'success')
        return redirect(url_for('customers.index'))
    
    return render_template('customers/add.html')

@customers_bp.route('/edit/<int:id>', methods=['GET', 'POST'])
@login_required
def edit(id):
    customer = Customer.query.get_or_404(id)
    
    if request.method == 'POST':
        customer.name = request.form['name']
        customer.phone = request.form['phone']
        customer.email = request.form.get('email', '')
        customer.address = request.form.get('address', '')
        
        db.session.commit()
        
        flash('تم تحديث بيانات العميل بنجاح', 'success')
        return redirect(url_for('customers.index'))
    
    return render_template('customers/edit.html', customer=customer)

@customers_bp.route('/delete/<int:id>', methods=['POST'])
@login_required
def delete(id):
    customer = Customer.query.get_or_404(id)
    
    # التحقق من عدم وجود مبيعات مرتبطة بالعميل
    if customer.sales:
        flash('لا يمكن حذف العميل لأنه مرتبط بعمليات بيع', 'danger')
        return redirect(url_for('customers.index'))
    
    db.session.delete(customer)
    db.session.commit()
    
    flash('تم حذف العميل بنجاح', 'success')
    return redirect(url_for('customers.index'))

@customers_bp.route('/view/<int:id>')
@login_required
def view(id):
    customer = Customer.query.get_or_404(id)
    return render_template('customers/view.html', customer=customer)
