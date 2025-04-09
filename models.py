from datetime import datetime
from app import db
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash

class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), index=True, unique=True)
    email = db.Column(db.String(120), index=True, unique=True)
    password_hash = db.Column(db.String(128))
    is_admin = db.Column(db.Boolean, default=False)
    full_name = db.Column(db.String(120))
    phone = db.Column(db.String(20))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # العلاقات
    sales = db.relationship('Sale', backref='seller', lazy='dynamic')
    expenses = db.relationship('Expense', backref='created_by', lazy='dynamic')
    
    def set_password(self, password):
        self.password_hash = generate_password_hash(password)
        
    def check_password(self, password):
        return check_password_hash(self.password_hash, password)
        
    def __repr__(self):
        return f'<User {self.username}>'

# نموذج الخدمة
class Service(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120), index=True)
    description = db.Column(db.Text)
    service_code = db.Column(db.String(20), unique=True)
    service_type = db.Column(db.String(50), index=True)
    duration = db.Column(db.Integer, default=60)  # مدة الخدمة بالدقائق
    price = db.Column(db.Float)
    category = db.Column(db.String(50), index=True)
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # العلاقات
    sale_items = db.relationship('SaleItem', backref='service', lazy='dynamic')
    
    def __repr__(self):
        return f'<Service {self.name}>'

# نموذج مقدمي الخدمة
class ServiceProvider(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120), index=True)
    specialization = db.Column(db.String(100))
    phone = db.Column(db.String(20))
    email = db.Column(db.String(120), nullable=True)
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def __repr__(self):
        return f'<ServiceProvider {self.name}>'

# نموذج العميل
class Customer(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120), index=True)
    phone = db.Column(db.String(20), index=True)
    email = db.Column(db.String(120), nullable=True)
    address = db.Column(db.Text, nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # العلاقات
    sales = db.relationship('Sale', backref='customer', lazy='dynamic')
    
    def __repr__(self):
        return f'<Customer {self.name}>'

# نموذج المبيعات
class Sale(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    invoice_number = db.Column(db.String(20), unique=True, index=True)
    customer_id = db.Column(db.Integer, db.ForeignKey('customer.id'), nullable=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    sale_date = db.Column(db.DateTime, default=datetime.utcnow)
    total_amount = db.Column(db.Float)
    discount = db.Column(db.Float, default=0)
    tax = db.Column(db.Float, default=0)
    final_amount = db.Column(db.Float)
    payment_method = db.Column(db.String(20))  # 'cash', 'card', 'transfer'
    payment_status = db.Column(db.String(20))  # 'paid', 'partial', 'unpaid'
    service_status = db.Column(db.String(20), default='scheduled')  # 'scheduled', 'in_progress', 'completed', 'cancelled'
    notes = db.Column(db.Text, nullable=True)
    
    # العلاقات
    items = db.relationship('SaleItem', backref='sale', lazy='dynamic', cascade='all, delete-orphan')
    payments = db.relationship('Payment', backref='sale', lazy='dynamic', cascade='all, delete-orphan')
    
    def __repr__(self):
        return f'<Sale {self.invoice_number}>'

# نموذج عناصر المبيعات
class SaleItem(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    sale_id = db.Column(db.Integer, db.ForeignKey('sale.id'))
    service_id = db.Column(db.Integer, db.ForeignKey('service.id'))
    quantity = db.Column(db.Integer)
    unit_price = db.Column(db.Float)
    discount = db.Column(db.Float, default=0)
    total_price = db.Column(db.Float)
    service_provider_id = db.Column(db.Integer, db.ForeignKey('service_provider.id'), nullable=True)
    scheduled_date = db.Column(db.DateTime, nullable=True)
    status = db.Column(db.String(20), default='scheduled')  # 'scheduled', 'in_progress', 'completed', 'cancelled'
    
    # العلاقات
    service_provider = db.relationship('ServiceProvider', backref='provided_services', lazy='dynamic')
    
    def __repr__(self):
        return f'<SaleItem {self.id}>'

# نموذج المدفوعات
class Payment(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    sale_id = db.Column(db.Integer, db.ForeignKey('sale.id'))
    amount = db.Column(db.Float)
    payment_method = db.Column(db.String(20))  # 'cash', 'card', 'transfer'
    payment_date = db.Column(db.DateTime, default=datetime.utcnow)
    reference = db.Column(db.String(50), nullable=True)  # مرجع للدفع (مثل رقم المعاملة)
    notes = db.Column(db.Text, nullable=True)
    
    def __repr__(self):
        return f'<Payment {self.id}>'

# نموذج المصروفات
class Expense(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(120))
    amount = db.Column(db.Float)
    expense_date = db.Column(db.DateTime, default=datetime.utcnow)
    category = db.Column(db.String(50), index=True)
    payment_method = db.Column(db.String(20))  # 'cash', 'card', 'transfer'
    reference = db.Column(db.String(50), nullable=True)  # مرجع للمصروف (مثل رقم الإيصال)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    notes = db.Column(db.Text, nullable=True)
    
    def __repr__(self):
        return f'<Expense {self.title}>'

# نموذج فئات المصروفات
class ExpenseCategory(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), unique=True)
    description = db.Column(db.Text, nullable=True)
    
    def __repr__(self):
        return f'<ExpenseCategory {self.name}>'
