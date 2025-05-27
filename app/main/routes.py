
from flask import Flask, render_template, redirect, url_for, flash, request, jsonify
from app.main import bp

from flask_login import login_required, logout_user, current_user
from app.models import *
from app.users.forms import EmptyForm


@bp.route('/')
@login_required
def index():
    page = request.args.get('page', 1, type=int)  # get page number from query string
    pagination = current_user.posts.order_by(Post.timestamp.desc()).paginate(page=page, per_page=25, error_out=False)
    posts = pagination.items
    form = EmptyForm()
    return render_template('index.html', title='Home', posts=posts, pagination=pagination, form=form)



@bp.route('/about')
def about():
    return render_template('about.html', title='About')



@bp.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('main.index'))