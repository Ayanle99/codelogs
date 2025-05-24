from flask import render_template, redirect, url_for, flash, request
from app.auth import bp
from app.auth.forms import LoginForm, RegisterForm
from app import db
from app.models import User
from werkzeug.security import generate_password_hash
from flask_login import login_user, current_user,logout_user
from werkzeug.security import check_password_hash


@bp.route('/login', methods=["GET", "POST"])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('main.index'))
    form = LoginForm()
    if form.validate_on_submit():
        username = form.username.data
        password = form.password.data
        user = User.query.filter_by(username=username).first()
        if user and check_password_hash(user.password_hash, password):
            login_user(user, remember=form.remember_me.data)
            flash(f'{user.username} logged in!', 'success')
            next_page = request.args.get('next')
            # security check
            if not next_page or not next_page.startswith('/'):
                next_page = url_for('main.index')
            return redirect(next_page)
        return redirect(url_for('main.index'))
    return render_template('auth/login.html', title="Login", form=form)


@bp.route('/register', methods=["GET", "POST"])
def register():
    form = RegisterForm()
    if form.validate_on_submit():
        # Check if user already exists by username or email
        user_by_username = User.query.filter_by(username=form.username.data).first()
        user_by_email = User.query.filter_by(email=form.email.data).first()
        if user_by_username:
            flash("Username already taken, please choose another.", "warning")
        elif user_by_email:
            flash("Email already registered, please login or use a different email.", "warning")
        else:
            # Create user with hashed password
            hashed_password = generate_password_hash(form.password.data)
            user = User(
                username=form.username.data,
                email=form.email.data,
                password_hash=hashed_password
            )
            db.session.add(user)
            db.session.commit()
            flash("Congratulations, you are now a registered user!", "success")
            return redirect(url_for('auth.login'))
    return render_template('auth/register.html', title="Register", form=form)
