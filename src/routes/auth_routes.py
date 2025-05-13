from flask import Blueprint, render_template, request, redirect, url_for, session, flash
from src.models.models import db, User
from werkzeug.security import generate_password_hash, check_password_hash

auth_bp = Blueprint("auth", __name__)

@auth_bp.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        username = request.form.get("username")
        email = request.form.get("email")
        password = request.form.get("password")

        if not username or not email or not password:
            flash("جميع الحقول مطلوبة", "danger")
            return redirect(url_for("auth.register"))

        existing_user_by_username = User.query.filter_by(username=username).first()
        if existing_user_by_username:
            flash("اسم المستخدم موجود بالفعل.", "danger")
            return redirect(url_for("auth.register"))

        existing_user_by_email = User.query.filter_by(email=email).first()
        if existing_user_by_email:
            flash("البريد الإلكتروني موجود بالفعل.", "danger")
            return redirect(url_for("auth.register"))

        new_user = User(username=username, email=email)
        new_user.set_password(password)
        db.session.add(new_user)
        db.session.commit()

        flash("تم إنشاء حسابك بنجاح! يمكنك الآن تسجيل الدخول.", "success")
        return redirect(url_for("auth.login"))
    
    # For GET request, render the registration page
    # We need to ensure the template path is correct. Assuming templates are in 'static/templates/'
    # If index.html is directly in static, then register.html should also be there or in a subfolder.
    # For now, let's assume a 'register.html' will be created in 'static/' directory.
    return render_template("register.html") 

@auth_bp.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        email = request.form.get("email")
        password = request.form.get("password")

        if not email or not password:
            flash("البريد الإلكتروني وكلمة المرور مطلوبان", "danger")
            return redirect(url_for("auth.login"))

        user = User.query.filter_by(email=email).first()

        if not user or not user.check_password(password):
            flash("البريد الإلكتروني أو كلمة المرور غير صحيحة.", "danger")
            return redirect(url_for("auth.login"))

        session["user_id"] = user.id
        session["username"] = user.username
        flash("تم تسجيل دخولك بنجاح!", "success")
        return redirect(url_for("serve", path="index.html")) # Redirect to homepage after login

    # For GET request, render the login page
    # Assuming a 'login.html' will be created in 'static/' directory.
    return render_template("login.html")

@auth_bp.route("/logout")
def logout():
    session.pop("user_id", None)
    session.pop("username", None)
    flash("تم تسجيل خروجك بنجاح.", "info")
    return redirect(url_for("auth.login"))

