
from flask import Flask, render_template, redirect, url_for, flash, request, jsonify
from app.main import bp
from app import db
from flask_login import login_required, logout_user, current_user
from app.models import *
from app.users.forms import EmptyForm
import logging
import os



logger = logging.getLogger(__name__)

from app.models import Post, followers



@bp.route('/')
@login_required
def index():
    page = request.args.get('page', 1, type=int)

    followed_posts = Post.query.join(
        followers, (followers.c.followed_id == Post.user_id)
    ).filter(
        followers.c.follower_id == current_user.id
    )

    own_posts = Post.query.filter_by(user_id=current_user.id)

    # Union followed and own posts, then order and paginate
    posts_query = followed_posts.union(own_posts).order_by(Post.timestamp.desc())

    pagination = posts_query.paginate(page=page, per_page=25, error_out=False)
    posts = pagination.items

    form = EmptyForm()

    logger.info("User %s accessed the index page (page %d)", current_user.username, page)
    return render_template('index.html', title='Home', posts=posts, pagination=pagination, form=form)



@bp.route('/about')
def about():
    logger.info("About page accessed from IP: %s", request.remote_addr)
    return render_template('about.html', title='About')



@bp.route('/logout')
@login_required
def logout():
    logger.info("User %s logged out", current_user.username)  # <-- log logout
    logout_user()
    return redirect(url_for('main.index'))