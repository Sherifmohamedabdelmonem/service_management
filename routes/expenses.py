from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_required, current_user
from models import Expense, ExpenseCategory
from app import db
from datetime import datetime

expenses_bp = Blueprint('expenses', __name__, url_prefix='/expenses')

@expenses_bp.route('/')
@login_required
def index():
    expenses = Expense.query.order_by(Expense.expense_date.desc()).all()
    return render_template('expenses.html', expenses=expenses)

@expenses_bp.route('/add', methods=['GET', 'POST'])
@login_required
def add():
    if request.method == 'POST':
        expense = Expense(
            title=request.form['title'],
            category=request.form['category'],
            amount=float(request.form['amount']),
            expense_date=datetime.strptime(request.form['expense_date'], '%Y-%m-%d'),
            payment_method=request.form['payment_method'],
            reference=request.form.get('reference', ''),
            user_id=current_user.id,
            notes=request.form.get('notes', '')
        )
        
        db.session.add(expense)
        db.session.commit()
        
        flash('تم إضافة المصروف بنجاح', 'success')
        return redirect(url_for('expenses.index'))
    
    categories = ExpenseCategory.query.all()
    return render_template('expenses/add.html', categories=categories)

@expenses_bp.route('/edit/<int:id>', methods=['GET', 'POST'])
@login_required
def edit(id):
    expense = Expense.query.get_or_404(id)
    
    if request.method == 'POST':
        expense.title = request.form['title']
        expense.category = request.form['category']
        expense.amount = float(request.form['amount'])
        expense.expense_date = datetime.strptime(request.form['expense_date'], '%Y-%m-%d')
        expense.payment_method = request.form['payment_method']
        expense.reference = request.form.get('reference', '')
        expense.notes = request.form.get('notes', '')
        
        db.session.commit()
        
        flash('تم تحديث المصروف بنجاح', 'success')
        return redirect(url_for('expenses.index'))
    
    categories = ExpenseCategory.query.all()
    return render_template('expenses/edit.html', expense=expense, categories=categories)

@expenses_bp.route('/delete/<int:id>', methods=['POST'])
@login_required
def delete(id):
    expense = Expense.query.get_or_404(id)
    
    db.session.delete(expense)
    db.session.commit()
    
    flash('تم حذف المصروف بنجاح', 'success')
    return redirect(url_for('expenses.index'))

@expenses_bp.route('/categories')
@login_required
def categories():
    categories = ExpenseCategory.query.all()
    return render_template('expenses/categories.html', categories=categories)

@expenses_bp.route('/categories/add', methods=['GET', 'POST'])
@login_required
def add_category():
    if request.method == 'POST':
        category = ExpenseCategory(
            name=request.form['name'],
            description=request.form.get('description', '')
        )
        
        db.session.add(category)
        db.session.commit()
        
        flash('تم إضافة فئة المصروفات بنجاح', 'success')
        return redirect(url_for('expenses.categories'))
    
    return render_template('expenses/add_category.html')

@expenses_bp.route('/categories/edit/<int:id>', methods=['GET', 'POST'])
@login_required
def edit_category(id):
    category = ExpenseCategory.query.get_or_404(id)
    
    if request.method == 'POST':
        category.name = request.form['name']
        category.description = request.form.get('description', '')
        
        db.session.commit()
        
        flash('تم تحديث فئة المصروفات بنجاح', 'success')
        return redirect(url_for('expenses.categories'))
    
    return render_template('expenses/edit_category.html', category=category)

@expenses_bp.route('/categories/delete/<int:id>', methods=['POST'])
@login_required
def delete_category(id):
    category = ExpenseCategory.query.get_or_404(id)
    
    # التحقق من عدم وجود مصروفات مرتبطة بالفئة
    if Expense.query.filter_by(category=category.name).first():
        flash('لا يمكن حذف الفئة لأنها مرتبطة بمصروفات', 'danger')
        return redirect(url_for('expenses.categories'))
    
    db.session.delete(category)
    db.session.commit()
    
    flash('تم حذف فئة المصروفات بنجاح', 'success')
    return redirect(url_for('expenses.categories'))
