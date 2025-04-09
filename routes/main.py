from flask import Blueprint, render_template, redirect, url_for
from flask_login import login_required

main_bp = Blueprint('main', __name__)

@main_bp.route('/')
@main_bp.route('/index')
def index():
    return render_template('index.html')

@main_bp.route('/dashboard')
@login_required
def dashboard():
    return render_template('dashboard.html')

# صفحات التقارير
@main_bp.route('/reports/sales')
@login_required
def sales_report():
    return render_template('reports/sales_report.html')

@main_bp.route('/reports/inventory')
@login_required
def inventory_report():
    return render_template('reports/inventory_report.html')
