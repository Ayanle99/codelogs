from flask import Flask, render_template, flash, url_for, redirect, request
from app.users import bp
from app.models import *


@bp.route('/user/<string:username>')
def user(username):
    user = User.query.filter_by(username=username).first()
    return render_template('users/user.html', title=f"{user.username} Profile",user=user)