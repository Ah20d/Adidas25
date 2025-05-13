from flask import Blueprint, render_template, request, redirect, url_for, session, flash
from src.models.models import db, ServiceCategory, Service, Order, User
from functools import wraps

services_bp = Blueprint("services", __name__)

# Decorator to check if user is logged in
def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if "user_id" not in session:
            flash("الرجاء تسجيل الدخول لعرض هذه الصفحة.", "warning")
            return redirect(url_for("auth.login"))
        return f(*args, **kwargs)
    return decorated_function

@services_bp.route("/categories")
@login_required
def list_categories():
    categories = ServiceCategory.query.all()
    # Assuming a template named 'service_categories.html' will be created in 'static/'
    return render_template("service_categories.html", categories=categories)

@services_bp.route("/category/<int:category_id>")
@login_required
def list_services_in_category(category_id):
    category = ServiceCategory.query.get_or_404(category_id)
    services = Service.query.filter_by(category_id=category.id).all()
    # Assuming a template named 'services_in_category.html' will be created in 'static/'
    return render_template("services_in_category.html", category=category, services=services)

@services_bp.route("/service/<int:service_id>")
@login_required
def service_details(service_id):
    service = Service.query.get_or_404(service_id)
    # Assuming a template named 'service_details.html' will be created in 'static/'
    return render_template("service_details.html", service=service)

@services_bp.route("/order/service/<int:service_id>", methods=["GET", "POST"])
@login_required
def place_order(service_id):
    service = Service.query.get_or_404(service_id)
    if request.method == "POST":
        quantity = int(request.form.get("quantity", 1))
        order_details_input = request.form.get("order_details_input") # e.g., link, username

        if quantity <= 0:
            flash("الكمية يجب أن تكون أكبر من صفر.", "danger")
            return redirect(url_for("services.service_details", service_id=service_id))
        
        total_price = service.price * quantity
        user_id = session["user_id"]

        new_order = Order(
            user_id=user_id,
            service_id=service.id,
            quantity=quantity,
            total_price=total_price,
            order_details_json=order_details_input # Store as plain text for now, consider JSON validation/parsing later
        )
        db.session.add(new_order)
        db.session.commit()

        flash(f"تم إنشاء طلبك لخدمة 	'{service.name}' بنجاح!", "success")
        return redirect(url_for("services.order_history"))

    # For GET request, show the order form (could be part of service_details.html or a new template)
    return render_template("place_order.html", service=service)

@services_bp.route("/orders")
@login_required
def order_history():
    user_id = session["user_id"]
    user_orders = Order.query.filter_by(user_id=user_id).order_by(Order.created_at.desc()).all()
    # Assuming a template named 'order_history.html' will be created in 'static/'
    return render_template("order_history.html", orders=user_orders)

