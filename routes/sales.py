from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_required, current_user
from models import Sale, SaleItem, Payment, Service, Customer, ServiceProvider
from app import db
from datetime import datetime

sales_bp = Blueprint('sales', __name__, url_prefix='/sales')

@sales_bp.route('/')
@login_required
def index():
    sales = Sale.query.order_by(Sale.sale_date.desc()).all()
    return render_template('sales.html', sales=sales)

@sales_bp.route('/add', methods=['GET', 'POST'])
@login_required
def add():
    if request.method == 'POST':
        # إنشاء رقم فاتورة جديد
        last_sale = Sale.query.order_by(Sale.id.desc()).first()
        if last_sale:
            invoice_number = f"INV-{int(last_sale.invoice_number.split('-')[1]) + 1:03d}"
        else:
            invoice_number = "INV-001"
        
        # إنشاء عملية البيع
        sale = Sale(
            invoice_number=invoice_number,
            customer_id=request.form.get('customer_id'),
            user_id=current_user.id,
            sale_date=datetime.strptime(request.form['sale_date'], '%Y-%m-%d'),
            total_amount=float(request.form['total_amount']),
            discount=float(request.form.get('discount', 0)),
            tax=float(request.form.get('tax', 0)),
            final_amount=float(request.form['final_amount']),
            payment_method=request.form['payment_method'],
            payment_status=request.form['payment_status'],
            service_status='scheduled',
            notes=request.form.get('notes', '')
        )
        
        db.session.add(sale)
        db.session.flush()  # للحصول على معرف البيع
        
        # إضافة عناصر البيع
        service_ids = request.form.getlist('service_id[]')
        quantities = request.form.getlist('quantity[]')
        unit_prices = request.form.getlist('unit_price[]')
        discounts = request.form.getlist('item_discount[]')
        total_prices = request.form.getlist('total_price[]')
        provider_ids = request.form.getlist('provider_id[]')
        scheduled_dates = request.form.getlist('scheduled_date[]')
        
        for i in range(len(service_ids)):
            service_id = int(service_ids[i])
            quantity = int(quantities[i])
            unit_price = float(unit_prices[i])
            discount = float(discounts[i]) if discounts[i] else 0
            total_price = float(total_prices[i])
            provider_id = int(provider_ids[i]) if provider_ids[i] else None
            scheduled_date = datetime.strptime(scheduled_dates[i], '%Y-%m-%dT%H:%M') if scheduled_dates[i] else None
            
            # إضافة عنصر البيع
            item = SaleItem(
                sale_id=sale.id,
                service_id=service_id,
                quantity=quantity,
                unit_price=unit_price,
                discount=discount,
                total_price=total_price,
                service_provider_id=provider_id,
                scheduled_date=scheduled_date,
                status='scheduled'
            )
            db.session.add(item)
        
        # إضافة المدفوعات إذا كانت الحالة مدفوعة أو مدفوعة جزئيًا
        if sale.payment_status in ['paid', 'partial'] and request.form.get('payment_amount'):
            payment = Payment(
                sale_id=sale.id,
                amount=float(request.form['payment_amount']),
                payment_date=datetime.strptime(request.form.get('payment_date', datetime.now().strftime('%Y-%m-%d')), '%Y-%m-%d'),
                payment_method=sale.payment_method,
                reference=request.form.get('payment_reference', ''),
                notes=request.form.get('payment_notes', '')
            )
            db.session.add(payment)
        
        db.session.commit()
        
        flash('تم إنشاء عملية البيع بنجاح', 'success')
        return redirect(url_for('sales.view', id=sale.id))
    
    services = Service.query.filter_by(is_active=True).all()
    customers = Customer.query.all()
    providers = ServiceProvider.query.filter_by(is_active=True).all()
    return render_template('sales/add.html', services=services, customers=customers, providers=providers)

@sales_bp.route('/view/<int:id>')
@login_required
def view(id):
    sale = Sale.query.get_or_404(id)
    return render_template('sales/view.html', sale=sale)

@sales_bp.route('/update_status/<int:id>', methods=['POST'])
@login_required
def update_status(id):
    sale = Sale.query.get_or_404(id)
    
    if request.method == 'POST':
        new_status = request.form['service_status']
        sale.service_status = new_status
        
        # تحديث حالة جميع عناصر البيع إذا تم تحديث حالة البيع الرئيسية
        if new_status in ['completed', 'cancelled']:
            for item in sale.items:
                item.status = new_status
        
        db.session.commit()
        
        flash('تم تحديث حالة الخدمة بنجاح', 'success')
        return redirect(url_for('sales.view', id=sale.id))
    
    return redirect(url_for('sales.view', id=sale.id))

@sales_bp.route('/update_item_status/<int:id>', methods=['POST'])
@login_required
def update_item_status(id):
    item = SaleItem.query.get_or_404(id)
    
    if request.method == 'POST':
        new_status = request.form['status']
        item.status = new_status
        
        # تحديث حالة البيع الرئيسية بناءً على حالة العناصر
        sale = item.sale
        all_completed = all(i.status == 'completed' for i in sale.items)
        any_in_progress = any(i.status == 'in_progress' for i in sale.items)
        
        if all_completed:
            sale.service_status = 'completed'
        elif any_in_progress:
            sale.service_status = 'in_progress'
        
        db.session.commit()
        
        flash('تم تحديث حالة عنصر الخدمة بنجاح', 'success')
        return redirect(url_for('sales.view', id=item.sale_id))
    
    return redirect(url_for('sales.view', id=item.sale_id))

@sales_bp.route('/add-payment/<int:id>', methods=['GET', 'POST'])
@login_required
def add_payment(id):
    sale = Sale.query.get_or_404(id)
    
    if sale.payment_status == 'paid':
        flash('تم دفع الفاتورة بالكامل بالفعل', 'info')
        return redirect(url_for('sales.view', id=sale.id))
    
    if request.method == 'POST':
        payment = Payment(
            sale_id=sale.id,
            amount=float(request.form['amount']),
            payment_date=datetime.strptime(request.form['payment_date'], '%Y-%m-%d'),
            payment_method=request.form['payment_method'],
            reference=request.form.get('reference', ''),
            notes=request.form.get('notes', '')
        )
        
        db.session.add(payment)
        
        # تحديث حالة الدفع
        total_paid = sum(p.amount for p in sale.payments) + payment.amount
        
        if total_paid >= sale.final_amount:
            sale.payment_status = 'paid'
        else:
            sale.payment_status = 'partial'
        
        db.session.commit()
        
        flash('تم إضافة الدفعة بنجاح', 'success')
        return redirect(url_for('sales.view', id=sale.id))
    
    return render_template('sales/add_payment.html', sale=sale)

@sales_bp.route('/print/<int:id>')
@login_required
def print_invoice(id):
    sale = Sale.query.get_or_404(id)
    return render_template('sales/print.html', sale=sale)

@sales_bp.route('/delete/<int:id>', methods=['POST'])
@login_required
def delete(id):
    sale = Sale.query.get_or_404(id)
    
    # حذف عناصر البيع والمدفوعات
    SaleItem.query.filter_by(sale_id=sale.id).delete()
    Payment.query.filter_by(sale_id=sale.id).delete()
    
    db.session.delete(sale)
    db.session.commit()
    
    flash('تم حذف عملية البيع بنجاح', 'success')
    return redirect(url_for('sales.index'))
