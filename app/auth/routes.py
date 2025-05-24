from flask import Flask, render_template, redirect, url_for, flash
from app.auth import bp
from app.auth.forms import LoginForm

@bp.route('/login', methods=["GET", "POST"])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        flash(f'Logged in user: {form.username.data}, remember me? {form.remember_me.data}')
        return redirect(url_for('main.index'))
    return render_template('auth/login.html', title="Login", form=form)

