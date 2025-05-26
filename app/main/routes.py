from flask import Flask, render_template, redirect, url_for, flash
from app.main import bp
from flask_login import login_required, logout_user

@bp.route('/')
@login_required
def index():
    return render_template('index.html', title='Home')



@bp.route('/about')
def about():
    return render_template('about.html', title='About')



@bp.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('main.index'))