from flask import Blueprint

bp = Blueprint('users', __name__,
               url_prefix='/users',
               template_folder='templates',
               static_folder='static')


from app.users import routes