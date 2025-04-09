from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_required, current_user
from models import Product, InventoryTransaction
from app import db
from datetime import datetime

products_bp = Blueprint('products', __name__, url_prefix='/products')

@products_bp.route('/')
@login_required
def index():
    products = Product.query.all()
    return render_template('products.html', products=products)

@products_bp.route('/add', methods=['GET', 'POST'])
@login_required
def add():
    if request.method == 'POST':
        product = Product(
            name=request.form['name'],
            description=request.form.get('description', ''),
            sku=request.form['sku'],
            category=request.form['category'],
            purchase_price=float(request.form['purchase_price']),
            selling_price=float(request.form['selling_price']),
            current_stock=int(request.form.get('current_stock', 0)),
            min_stock_level=int(request.form.get('min_stock_level', 5))
        )
        
        db.session.add(product)
        db.session.commit()
        
        # إذا كان هناك مخزون أولي، قم بتسجيل حركة مخزون
        if product.current_stock > 0:
            inventory_transaction = InventoryTransaction(
                product_id=product.id,
                transaction_type='in',
                quantity=product.current_stock,
                reference='مخزون أولي',
                notes='إضافة مخزون أولي عند إنشاء المنتج'
            )
            db.session.add(inventory_transaction)
            db.session.commit()
        
        flash('تم إضافة المنتج بنجاح', 'success')
        return redirect(url_for('products.index'))
    
    return render_template('products/add.html')

@products_bp.route('/edit/<int:id>', methods=['GET', 'POST'])
@login_required
def edit(id):
    product = Product.query.get_or_404(id)
    
    if request.method == 'POST':
        product.name = request.form['name']
        product.description = request.form.get('description', '')
        product.sku = request.form['sku']
        product.category = request.form['category']
        product.purchase_price = float(request.form['purchase_price'])
        product.selling_price = float(request.form['selling_price'])
        product.min_stock_level = int(request.form['min_stock_level'])
        
        db.session.commit()
        
        flash('تم تحديث المنتج بنجاح', 'success')
        return redirect(url_for('products.index'))
    
    return render_template('products/edit.html', product=product)

@products_bp.route('/delete/<int:id>', methods=['POST'])
@login_required
def delete(id):
    product = Product.query.get_or_404(id)
    
    # التحقق من عدم وجود مبيعات مرتبطة بالمنتج
    if product.sale_items:
        flash('لا يمكن حذف المنتج لأنه مرتبط بعمليات بيع', 'danger')
        return redirect(url_for('products.index'))
    
    # حذف حركات المخزون المرتبطة بالمنتج
    InventoryTransaction.query.filter_by(product_id=product.id).delete()
    
    db.session.delete(product)
    db.session.commit()
    
    flash('تم حذف المنتج بنجاح', 'success')
    return redirect(url_for('products.index'))

@products_bp.route('/add-stock/<int:id>', methods=['GET', 'POST'])
@login_required
def add_stock(id):
    product = Product.query.get_or_404(id)
    
    if request.method == 'POST':
        quantity = int(request.form['quantity'])
        reference = request.form.get('reference', '')
        notes = request.form.get('notes', '')
        
        # تحديث المخزون
        product.current_stock += quantity
        
        # تسجيل حركة المخزون
        inventory_transaction = InventoryTransaction(
            product_id=product.id,
            transaction_type='in',
            quantity=quantity,
            reference=reference,
            notes=notes
        )
        
        db.session.add(inventory_transaction)
        db.session.commit()
        
        flash(f'تم إضافة {quantity} وحدة إلى مخزون {product.name}', 'success')
        return redirect(url_for('products.index'))
    
    return render_template('products/add_stock.html', product=product)

@products_bp.route('/inventory-transactions')
@login_required
def inventory_transactions():
    transactions = InventoryTransaction.query.order_by(InventoryTransaction.created_at.desc()).all()
    return render_template('products/inventory_transactions.html', transactions=transactions)
