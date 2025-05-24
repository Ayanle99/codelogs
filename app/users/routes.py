from app.models import User
from flask_login import login_required
from flask import render_template
from app.users import bp

@bp.route('/user/<string:username>')
@login_required
def user(username):
    user = User.query.filter_by(username=username).first_or_404()
    return render_template('users/user.html', title=f"{user.username} Profile", user=user)
