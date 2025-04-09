from flask import Blueprint, jsonify, request
from models import Product, Customer, Sale, SaleItem, Payment, Expense, InventoryTransaction
from app import db
from datetime import datetime

api_bp = Blueprint('api', __name__)

# API للمنتجات
@api_bp.route('/products', methods=['GET'])
def get_products():
    products = Product.query.all()
    return jsonify({
        'products': [
            {
                'id': product.id,
                'name': product.name,
                'description': product.description,
                'sku': product.sku,
                'category': product.category,
                'purchase_price': product.purchase_price,
                'selling_price': product.selling_price,
                'current_stock': product.current_stock,
                'min_stock_level': product.min_stock_level
            } for product in products
        ]
    })

@api_bp.route('/products/<int:id>', methods=['GET'])
def get_product(id):
    product = Product.query.get_or_404(id)
    return jsonify({
        'id': product.id,
        'name': product.name,
        'description': product.description,
        'sku': product.sku,
        'category': product.category,
        'purchase_price': product.purchase_price,
        'selling_price': product.selling_price,
        'current_stock': product.current_stock,
        'min_stock_level': product.min_stock_level
    })

@api_bp.route('/products', methods=['POST'])
def create_product():
    data = request.get_json() or {}
    product = Product(
        name=data['name'],
        description=data.get('description', ''),
        sku=data['sku'],
        category=data['category'],
        purchase_price=data['purchase_price'],
        selling_price=data['selling_price'],
        current_stock=data.get('current_stock', 0),
        min_stock_level=data.get('min_stock_level', 5)
    )
    db.session.add(product)
    db.session.commit()
    return jsonify({
        'id': product.id,
        'name': product.name,
        'message': 'تم إضافة المنتج بنجاح'
    }), 201

@api_bp.route('/products/<int:id>', methods=['PUT'])
def update_product(id):
    product = Product.query.get_or_404(id)
    data = request.get_json() or {}
    
    if 'name' in data:
        product.name = data['name']
    if 'description' in data:
        product.description = data['description']
    if 'sku' in data:
        product.sku = data['sku']
    if 'category' in data:
        product.category = data['category']
    if 'purchase_price' in data:
        product.purchase_price = data['purchase_price']
    if 'selling_price' in data:
        product.selling_price = data['selling_price']
    if 'current_stock' in data:
        product.current_stock = data['current_stock']
    if 'min_stock_level' in data:
        product.min_stock_level = data['min_stock_level']
    
    db.session.commit()
    return jsonify({
        'id': product.id,
        'name': product.name,
        'message': 'تم تحديث المنتج بنجاح'
    })

@api_bp.route('/products/<int:id>', methods=['DELETE'])
def delete_product(id):
    product = Product.query.get_or_404(id)
    db.session.delete(product)
    db.session.commit()
    return jsonify({
        'message': 'تم حذف المنتج بنجاح'
    })

# API للعملاء
@api_bp.route('/customers', methods=['GET'])
def get_customers():
    customers = Customer.query.all()
    return jsonify({
        'customers': [
            {
                'id': customer.id,
                'name': customer.name,
                'phone': customer.phone,
                'email': customer.email,
                'address': customer.address
            } for customer in customers
        ]
    })

@api_bp.route('/customers/<int:id>', methods=['GET'])
def get_customer(id):
    customer = Customer.query.get_or_404(id)
    return jsonify({
        'id': customer.id,
        'name': customer.name,
        'phone': customer.phone,
        'email': customer.email,
        'address': customer.address
    })

@api_bp.route('/customers', methods=['POST'])
def create_customer():
    data = request.get_json() or {}
    customer = Customer(
        name=data['name'],
        phone=data['phone'],
        email=data.get('email', ''),
        address=data.get('address', '')
    )
    db.session.add(customer)
    db.session.commit()
    return jsonify({
        'id': customer.id,
        'name': customer.name,
        'message': 'تم إضافة العميل بنجاح'
    }), 201

@api_bp.route('/customers/<int:id>', methods=['PUT'])
def update_customer(id):
    customer = Customer.query.get_or_404(id)
    data = request.get_json() or {}
    
    if 'name' in data:
        customer.name = data['name']
    if 'phone' in data:
        customer.phone = data['phone']
    if 'email' in data:
        customer.email = data['email']
    if 'address' in data:
        customer.address = data['address']
    
    db.session.commit()
    return jsonify({
        'id': customer.id,
        'name': customer.name,
        'message': 'تم تحديث بيانات العميل بنجاح'
    })

@api_bp.route('/customers/<int:id>', methods=['DELETE'])
def delete_customer(id):
    customer = Customer.query.get_or_404(id)
    db.session.delete(customer)
    db.session.commit()
    return jsonify({
        'message': 'تم حذف العميل بنجاح'
    })

# API للمبيعات
@api_bp.route('/sales', methods=['GET'])
def get_sales():
    sales = Sale.query.all()
    return jsonify({
        'sales': [
            {
                'id': sale.id,
                'invoice_number': sale.invoice_number,
                'customer_name': sale.customer.name if sale.customer else '',
                'sale_date': sale.sale_date.isoformat(),
                'total_amount': sale.total_amount,
                'final_amount': sale.final_amount,
                'payment_status': sale.payment_status
            } for sale in sales
        ]
    })

@api_bp.route('/sales/<int:id>', methods=['GET'])
def get_sale(id):
    sale = Sale.query.get_or_404(id)
    return jsonify({
        'id': sale.id,
        'invoice_number': sale.invoice_number,
        'customer_id': sale.customer_id,
        'customer_name': sale.customer.name if sale.customer else '',
        'sale_date': sale.sale_date.isoformat(),
        'total_amount': sale.total_amount,
        'discount': sale.discount,
        'tax': sale.tax,
        'final_amount': sale.final_amount,
        'payment_method': sale.payment_method,
        'payment_status': sale.payment_status,
        'notes': sale.notes,
        'items': [
            {
                'id': item.id,
                'product_id': item.product_id,
                'product_name': item.product.name,
                'quantity': item.quantity,
                'unit_price': item.unit_price,
                'discount': item.discount,
                'total_price': item.total_price
            } for item in sale.items
        ],
        'payments': [
            {
                'id': payment.id,
                'amount': payment.amount,
                'payment_date': payment.payment_date.isoformat(),
                'payment_method': payment.payment_method,
                'reference': payment.reference
            } for payment in sale.payments
        ]
    })

@api_bp.route('/sales', methods=['POST'])
def create_sale():
    data = request.get_json() or {}
    
    # إنشاء رقم فاتورة جديد
    last_sale = Sale.query.order_by(Sale.id.desc()).first()
    if last_sale:
        invoice_number = f"INV-{int(last_sale.invoice_number.split('-')[1]) + 1:03d}"
    else:
        invoice_number = "INV-001"
    
    sale = Sale(
        invoice_number=invoice_number,
        customer_id=data.get('customer_id'),
        user_id=1,  # يجب تغييره لاستخدام المستخدم الحالي
        sale_date=datetime.fromisoformat(data.get('sale_date', datetime.now().isoformat())),
        total_amount=data['total_amount'],
        discount=data.get('discount', 0),
        tax=data.get('tax', 0),
        final_amount=data['final_amount'],
        payment_method=data['payment_method'],
        payment_status=data['payment_status'],
        notes=data.get('notes', '')
    )
    db.session.add(sale)
    db.session.flush()  # للحصول على معرف البيع
    
    # إضافة عناصر البيع
    for item_data in data['items']:
        item = SaleItem(
            sale_id=sale.id,
            product_id=item_data['product_id'],
            quantity=item_data['quantity'],
            unit_price=item_data['unit_price'],
            discount=item_data.get('discount', 0),
            total_price=item_data['total_price']
        )
        db.session.add(item)
        
        # تحديث المخزون
        product = Product.query.get(item_data['product_id'])
        product.current_stock -= item_data['quantity']
        
        # تسجيل حركة المخزون
        inventory_transaction = InventoryTransaction(
            product_id=item_data['product_id'],
            transaction_type='out',
            quantity=item_data['quantity'],
            reference=invoice_number,
            notes=f"سحب من المخزون لعملية البيع {invoice_number}"
        )
        db.session.add(inventory_transaction)
    
    # إضافة المدفوعات إذا كانت الحالة مدفوعة أو مدفوعة جزئيًا
    if data['payment_status'] in ['paid', 'partial'] and data.get('payment_amount'):
        payment = Payment(
            sale_id=sale.id,
            amount=data['payment_amount'],
            payment_date=datetime.fromisoformat(data.get('payment_date', datetime.now().isoformat())),
            payment_method=data['payment_method'],
            reference=data.get('payment_reference', ''),
            notes=data.get('payment_notes', '')
        )
        db.session.add(payment)
    
    db.session.commit()
    return jsonify({
        'id': sale.id,
        'invoice_number': sale.invoice_number,
        'message': 'تم إنشاء عملية البيع بنجاح'
    }), 201

# API للمصروفات
@api_bp.route('/expenses', methods=['GET'])
def get_expenses():
    expenses = Expense.query.all()
    return jsonify({
        'expenses': [
            {
                'id': expense.id,
                'title': expense.title,
                'category': expense.category,
                'amount': expense.amount,
                'expense_date': expense.expense_date.isoformat(),
                'payment_method': expense.payment_method
            } for expense in expenses
        ]
    })

@api_bp.route('/expenses/<int:id>', methods=['GET'])
def get_expense(id):
    expense = Expense.query.get_or_404(id)
    return jsonify({
        'id': expense.id,
        'title': expense.title,
        'category': expense.category,
        'amount': expense.amount,
        'expense_date': expense.expense_date.isoformat(),
        'payment_method': expense.payment_method,
        'reference': expense.reference,
        'notes': expense.notes
    })

@api_bp.route('/expenses', methods=['POST'])
def create_expense():
    data = request.get_json() or {}
    expense = Expense(
        title=data['title'],
        category=data['category'],
        amount=data['amount'],
        expense_date=datetime.fromisoformat(data.get('expense_date', datetime.now().isoformat())),
        payment_method=data['payment_method'],
        reference=data.get('reference', ''),
        user_id=1,  # يجب تغييره لاستخدام المستخدم الحالي
        notes=data.get('notes', '')
    )
    db.session.add(expense)
    db.session.commit()
    return jsonify({
        'id': expense.id,
        'title': expense.title,
        'message': 'تم إضافة المصروف بنجاح'
    }), 201

@api_bp.route('/expenses/<int:id>', methods=['PUT'])
def update_expense(id):
    expense = Expense.query.get_or_404(id)
    data = request.get_json() or {}
    
    if 'title' in data:
        expense.title = data['title']
    if 'category' in data:
        expense.category = data['category']
    if 'amount' in data:
        expense.amount = data['amount']
    if 'expense_date' in data:
        expense.expense_date = datetime.fromisoformat(data['expense_date'])
    if 'payment_method' in data:
        expense.payment_method = data['payment_method']
    if 'reference' in data:
        expense.reference = data['reference']
    if 'notes' in data:
        expense.notes = data['notes']
    
    db.session.commit()
    return jsonify({
        'id': expense.id,
        'title': expense.title,
        'message': 'تم تحديث المصروف بنجاح'
    })

@api_bp.route('/expenses/<int:id>', methods=['DELETE'])
def delete_expense(id):
    expense = Expense.query.get_or_404(id)
    db.session.delete(expense)
    db.session.commit()
    return jsonify({
        'message': 'تم حذف المصروف بنجاح'
    })

# API للتقارير
@api_bp.route('/reports/sales', methods=['GET'])
def sales_report():
    # هنا سيتم تنفيذ منطق تقرير المبيعات الفعلي
    # هذا مجرد بيانات تجريبية للاختبار
    
    return jsonify({
        'summary': {
            'total_sales': 5000.0,
            'invoice_count': 20,
            'average_invoice': 250.0,
            'total_profit': 2000.0
        },
        'sales_by_time': [
            {'period': 'يناير', 'total': 1200.0},
            {'period': 'فبراير', 'total': 1500.0},
            {'period': 'مارس', 'total': 1800.0},
            {'period': 'أبريل', 'total': 500.0}
        ],
        'sales_by_product': [
            {'product_name': 'منتج 1', 'total': 2000.0},
            {'product_name': 'منتج 2', 'total': 1500.0},
            {'product_name': 'منتج 3', 'total': 1000.0},
            {'product_name': 'منتج 4', 'total': 500.0}
        ],
        'top_customers': [
            {'customer_name': 'عميل 1', 'total': 2000.0},
            {'customer_name': 'عميل 2', 'total': 1500.0},
            {'customer_name': 'عميل 3', 'total': 1000.0}
        ],
        'sales_by_payment_method': [
            {'payment_method': 'cash', 'total': 3000.0},
            {'payment_method': 'card', 'total': 1500.0},
            {'payment_method': 'transfer', 'total': 500.0}
        ],
        'sales': [
            {
                'invoice_number': 'INV-001',
                'sale_date': '2025-04-01T10:00:00',
                'customer_name': 'عميل 1',
                'items': [
                    {'product_name': 'منتج 1', 'quantity': 2}
                ],
                'total_amount': 300.0,
                'discount': 0.0,
                'final_amount': 300.0,
                'payment_method': 'cash',
                'payment_status': 'paid'
            },
            {
                'invoice_number': 'INV-002',
                'sale_date': '2025-04-02T11:00:00',
                'customer_name': 'عميل 2',
                'items': [
                    {'product_name': 'منتج 2', 'quantity': 1}
                ],
                'total_amount': 150.0,
                'discount': 0.0,
                'final_amount': 150.0,
                'payment_method': 'card',
                'payment_status': 'paid'
            }
        ]
    })

@api_bp.route('/reports/inventory', methods=['GET'])
def inventory_report():
    # هنا سيتم تنفيذ منطق تقرير المخزون الفعلي
    # هذا مجرد بيانات تجريبية للاختبار
    
    return jsonify({
        'summary': {
            'total_products': 50,
            'inventory_value': 15000.0,
            'low_stock_count': 5,
            'out_of_stock_count': 2
        },
        'stock_by_category': [
            {'category': 'إلكترونيات', 'stock_count': 20},
            {'category': 'ملابس', 'stock_count': 15},
            {'category': 'أثاث', 'stock_count': 10},
            {'category': 'أخرى', 'stock_count': 5}
        ],
        'top_products_by_value': [
            {'product_name': 'منتج 1', 'stock_value': 5000.0},
            {'product_name': 'منتج 2', 'stock_value': 3000.0},
            {'product_name': 'منتج 3', 'stock_value': 2000.0}
        ],
        'top_selling_products': [
            {'product_name': 'منتج 1', 'sales_count': 50},
            {'product_name': 'منتج 2', 'sales_count': 30},
            {'product_name': 'منتج 3', 'sales_count': 20}
        ],
        'monthly_inventory_movement': [
            {'month': 'يناير', 'stock_in': 100, 'stock_out': 80},
            {'month': 'فبراير', 'stock_in': 90, 'stock_out': 70},
            {'month': 'مارس', 'stock_in': 80, 'stock_out': 60},
            {'month': 'أبريل', 'stock_in': 70, 'stock_out': 50}
        ],
        'products': [
            {
                'code': 'P001',
                'name': 'منتج 1',
                'category': 'إلكترونيات',
                'current_stock': 50,
                'min_stock': 10,
                'cost_price': 100.0,
                'selling_price': 150.0,
                'stock_value': 5000.0,
                'last_updated': '2025-04-01T10:00:00'
            },
            {
                'code': 'P002',
                'name': 'منتج 2',
                'category': 'ملابس',
                'current_stock': 30,
                'min_stock': 5,
                'cost_price': 50.0,
                'selling_price': 80.0,
                'stock_value': 1500.0,
                'last_updated': '2025-04-01T10:00:00'
            }
        ],
        'alerts': [
            {
                'type': 'low_stock',
                'product_name': 'منتج 3',
                'current_stock': 3,
                'min_stock': 5
            },
            {
                'type': 'out_of_stock',
                'product_name': 'منتج 4'
            }
        ]
    })

# API لفئات المنتجات
@api_bp.route('/product-categories', methods=['GET'])
def get_product_categories():
    # استخراج الفئات الفريدة من جدول المنتجات
    categories = db.session.query(Product.category).distinct().all()
    return jsonify({
        'categories': [
            {'name': category[0]} for category in categories
        ]
    })
