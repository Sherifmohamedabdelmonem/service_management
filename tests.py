#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import sys
import unittest
import tempfile
import json
from datetime import datetime, timedelta

# إضافة المجلد الحالي إلى مسار البحث
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# استيراد التطبيق
from app import create_app, db
from models import User, Product, Customer, Sale, SaleItem, Payment, Expense, ExpenseCategory, InventoryTransaction

class BusinessManagementSystemTestCase(unittest.TestCase):
    """اختبارات وحدة لنظام إدارة الأعمال"""

    def setUp(self):
        """إعداد بيئة الاختبار قبل كل اختبار"""
        self.db_fd, db_path = tempfile.mkstemp()
        self.app = create_app()
        self.app.config['TESTING'] = True
        self.app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + db_path
        self.app.config['WTF_CSRF_ENABLED'] = False
        self.client = self.app.test_client()
        
        with self.app.app_context():
            db.create_all()
            self._create_test_data()

    def tearDown(self):
        """تنظيف بيئة الاختبار بعد كل اختبار"""
        with self.app.app_context():
            db.session.remove()
            db.drop_all()
        os.close(self.db_fd)
        os.unlink(self.app.config['SQLALCHEMY_DATABASE_URI'].replace('sqlite:///', ''))

    def _create_test_data(self):
        """إنشاء بيانات اختبار"""
        # إنشاء مستخدم اختبار
        test_user = User(
            username='admin',
            email='admin@example.com',
            full_name='مدير النظام'
        )
        test_user.set_password('password')
        db.session.add(test_user)
        
        # إنشاء فئات مصروفات
        categories = ['إيجار', 'رواتب', 'مرافق', 'تسويق', 'أخرى']
        for category_name in categories:
            category = ExpenseCategory(name=category_name)
            db.session.add(category)
        
        # إنشاء منتجات اختبار
        products = [
            Product(
                name='منتج 1',
                description='وصف المنتج 1',
                sku='P001',
                category='إلكترونيات',
                purchase_price=100.0,
                selling_price=150.0,
                current_stock=50,
                min_stock_level=10
            ),
            Product(
                name='منتج 2',
                description='وصف المنتج 2',
                sku='P002',
                category='ملابس',
                purchase_price=50.0,
                selling_price=80.0,
                current_stock=30,
                min_stock_level=5
            ),
            Product(
                name='منتج 3',
                description='وصف المنتج 3',
                sku='P003',
                category='إلكترونيات',
                purchase_price=200.0,
                selling_price=300.0,
                current_stock=20,
                min_stock_level=5
            )
        ]
        for product in products:
            db.session.add(product)
        
        # إنشاء عملاء اختبار
        customers = [
            Customer(
                name='عميل 1',
                phone='0123456789',
                email='customer1@example.com',
                address='عنوان العميل 1'
            ),
            Customer(
                name='عميل 2',
                phone='0987654321',
                email='customer2@example.com',
                address='عنوان العميل 2'
            )
        ]
        for customer in customers:
            db.session.add(customer)
        
        # حفظ التغييرات لإنشاء المعرفات
        db.session.commit()
        
        # إنشاء مبيعات اختبار
        sale1 = Sale(
            invoice_number='INV-001',
            customer_id=customers[0].id,
            user_id=test_user.id,
            sale_date=datetime.now(),
            total_amount=230.0,
            discount=0.0,
            tax=0.0,
            final_amount=230.0,
            payment_method='cash',
            payment_status='paid',
            notes='ملاحظات عملية البيع 1'
        )
        db.session.add(sale1)
        
        sale2 = Sale(
            invoice_number='INV-002',
            customer_id=customers[1].id,
            user_id=test_user.id,
            sale_date=datetime.now() - timedelta(days=1),
            total_amount=300.0,
            discount=20.0,
            tax=0.0,
            final_amount=280.0,
            payment_method='card',
            payment_status='paid',
            notes='ملاحظات عملية البيع 2'
        )
        db.session.add(sale2)
        
        # حفظ التغييرات لإنشاء المعرفات
        db.session.commit()
        
        # إنشاء عناصر المبيعات
        sale_items = [
            SaleItem(
                sale_id=sale1.id,
                product_id=products[0].id,
                quantity=1,
                unit_price=150.0,
                discount=0.0,
                total_price=150.0
            ),
            SaleItem(
                sale_id=sale1.id,
                product_id=products[1].id,
                quantity=1,
                unit_price=80.0,
                discount=0.0,
                total_price=80.0
            ),
            SaleItem(
                sale_id=sale2.id,
                product_id=products[2].id,
                quantity=1,
                unit_price=300.0,
                discount=20.0,
                total_price=280.0
            )
        ]
        for item in sale_items:
            db.session.add(item)
        
        # إنشاء مدفوعات
        payment1 = Payment(
            sale_id=sale1.id,
            amount=230.0,
            payment_date=datetime.now(),
            payment_method='cash',
            reference='',
            notes=''
        )
        db.session.add(payment1)
        
        payment2 = Payment(
            sale_id=sale2.id,
            amount=280.0,
            payment_date=datetime.now() - timedelta(days=1),
            payment_method='card',
            reference='CARD-123456',
            notes=''
        )
        db.session.add(payment2)
        
        # إنشاء مصروفات
        expense1 = Expense(
            title='إيجار المحل',
            category='إيجار',
            amount=1000.0,
            expense_date=datetime.now() - timedelta(days=5),
            payment_method='transfer',
            reference='TRF-123456',
            notes='إيجار شهر أبريل',
            user_id=test_user.id
        )
        db.session.add(expense1)
        
        expense2 = Expense(
            title='فاتورة كهرباء',
            category='مرافق',
            amount=200.0,
            expense_date=datetime.now() - timedelta(days=3),
            payment_method='cash',
            reference='',
            notes='فاتورة كهرباء شهر مارس',
            user_id=test_user.id
        )
        db.session.add(expense2)
        
        # إنشاء حركات المخزون
        inventory_transaction1 = InventoryTransaction(
            product_id=products[0].id,
            transaction_type='in',
            quantity=50,
            reference='PO-001',
            notes='استلام مخزون أولي',
            transaction_date=datetime.now() - timedelta(days=10)
        )
        db.session.add(inventory_transaction1)
        
        inventory_transaction2 = InventoryTransaction(
            product_id=products[1].id,
            transaction_type='in',
            quantity=30,
            reference='PO-002',
            notes='استلام مخزون أولي',
            transaction_date=datetime.now() - timedelta(days=10)
        )
        db.session.add(inventory_transaction2)
        
        inventory_transaction3 = InventoryTransaction(
            product_id=products[2].id,
            transaction_type='in',
            quantity=20,
            reference='PO-003',
            notes='استلام مخزون أولي',
            transaction_date=datetime.now() - timedelta(days=10)
        )
        db.session.add(inventory_transaction3)
        
        # حفظ جميع التغييرات
        db.session.commit()

    def test_login(self):
        """اختبار تسجيل الدخول"""
        response = self.client.post('/login', data={
            'username': 'admin',
            'password': 'password'
        }, follow_redirects=True)
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'dashboard', response.data)

    def test_products_api(self):
        """اختبار واجهة برمجة التطبيقات للمنتجات"""
        # اختبار جلب المنتجات
        response = self.client.get('/api/products')
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertEqual(len(data['products']), 3)
        
        # اختبار إضافة منتج جديد
        response = self.client.post('/api/products', json={
            'name': 'منتج جديد',
            'description': 'وصف المنتج الجديد',
            'code': 'P004',
            'category': 'أثاث',
            'cost_price': 300.0,
            'selling_price': 450.0,
            'current_stock': 10,
            'min_stock': 2
        })
        self.assertEqual(response.status_code, 201)
        
        # التحقق من إضافة المنتج
        response = self.client.get('/api/products')
        data = json.loads(response.data)
        self.assertEqual(len(data['products']), 4)
        
        # اختبار تحديث منتج
        response = self.client.put('/api/products/1', json={
            'name': 'منتج 1 محدث',
            'selling_price': 160.0
        })
        self.assertEqual(response.status_code, 200)
        
        # التحقق من تحديث المنتج
        response = self.client.get('/api/products/1')
        data = json.loads(response.data)
        self.assertEqual(data['name'], 'منتج 1 محدث')
        self.assertEqual(data['selling_price'], 160.0)

    def test_customers_api(self):
        """اختبار واجهة برمجة التطبيقات للعملاء"""
        # اختبار جلب العملاء
        response = self.client.get('/api/customers')
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertEqual(len(data['customers']), 2)
        
        # اختبار إضافة عميل جديد
        response = self.client.post('/api/customers', json={
            'name': 'عميل جديد',
            'phone': '0555555555',
            'email': 'newcustomer@example.com',
            'address': 'عنوان العميل الجديد'
        })
        self.assertEqual(response.status_code, 201)
        
        # التحقق من إضافة العميل
        response = self.client.get('/api/customers')
        data = json.loads(response.data)
        self.assertEqual(len(data['customers']), 3)
        
        # اختبار تحديث عميل
        response = self.client.put('/api/customers/1', json={
            'name': 'عميل 1 محدث',
            'phone': '0123456780'
        })
        self.assertEqual(response.status_code, 200)
        
        # التحقق من تحديث العميل
        response = self.client.get('/api/customers/1')
        data = json.loads(response.data)
        self.assertEqual(data['name'], 'عميل 1 محدث')
        self.assertEqual(data['phone'], '0123456780')

    def test_sales_api(self):
        """اختبار واجهة برمجة التطبيقات للمبيعات"""
        # اختبار جلب المبيعات
        response = self.client.get('/api/sales')
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertEqual(len(data['sales']), 2)
        
        # اختبار إضافة عملية بيع جديدة
        response = self.client.post('/api/sales', json={
            'customer_id': 1,
            'sale_date': datetime.now().isoformat(),
            'payment_method': 'cash',
            'payment_status': 'paid',
            'items': [
                {
                    'product_id': 1,
                    'quantity': 2,
                    'unit_price': 150.0,
                    'discount': 0.0,
                    'total_price': 300.0
                }
            ],
            'total_amount': 300.0,
            'discount': 0.0,
            'tax': 0.0,
            'final_amount': 300.0,
            'notes': 'عملية بيع جديدة'
        })
        self.assertEqual(response.status_code, 201)
        
        # التحقق من إضافة عملية البيع
        response = self.client.get('/api/sales')
        data = json.loads(response.data)
        self.assertEqual(len(data['sales']), 3)
        
        # اختبار جلب تفاصيل عملية بيع
        response = self.client.get('/api/sales/1')
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertEqual(data['invoice_number'], 'INV-001')
        self.assertEqual(len(data['items']), 2)

    def test_expenses_api(self):
        """اختبار واجهة برمجة التطبيقات للمصروفات"""
        # اختبار جلب المصروفات
        response = self.client.get('/api/expenses')
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertEqual(len(data['expenses']), 2)
        
        # اختبار إضافة مصروف جديد
        response = self.client.post('/api/expenses', json={
            'title': 'مصروف جديد',
            'category': 'أخرى',
            'amount': 150.0,
            'expense_date': datetime.now().isoformat(),
            'payment_method': 'cash',
            'notes': 'مصروف جديد للاختبار'
        })
        self.assertEqual(response.status_code, 201)
        
        # التحقق من إضافة المصروف
        response = self.client.get('/api/expenses')
        data = json.loads(response.data)
        self.assertEqual(len(data['expenses']), 3)
        
        # اختبار تحديث مصروف
        response = self.client.put('/api/expenses/1', json={
            'title': 'إيجار المحل المحدث',
            'amount': 1100.0
        })
        self.assertEqual(response.status_code, 200)
        
        # التحقق من تحديث المصروف
        response = self.client.get('/api/expenses/1')
        data = json.loads(response.data)
        self.assertEqual(data['title'], 'إيجار المحل المحدث')
        self.assertEqual(data['amount'], 1100.0)

    def test_reports_api(self):
        """اختبار واجهة برمجة التطبيقات للتقارير"""
        # اختبار تقرير المبيعات
        response = self.client.get('/api/reports/sales')
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertIn('summary', data)
        self.assertIn('sales', data)
        
        # اختبار تقرير المخزون
        response = self.client.get('/api/reports/inventory')
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertIn('summary', data)
        self.assertIn('products', data)

if __name__ == '__main__':
    unittest.main()
