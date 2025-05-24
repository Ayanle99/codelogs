from flask import Flask, render_template, redirect, url_for, flash
from app.main import bp
from flask import redirect, url_for, flash
from flask_login import logout_user, login_required
from app.models import *
from flask_login import current_user


@bp.route('/')
@login_required
def index():
    return render_template('index.html', title='Home',user=current_user)



@bp.route('/about')
def about():
    user = {
        'author': 'max',
        'email': 'max@example.com',
        'info': 'About Page'
    }
    return render_template('about.html', title='About', user=user)


@bp.route('/logout')
@login_required
def logout():
    logout_user()
    flash('You have been logged out.', 'info')
    return redirect(url_for('main.index'))
