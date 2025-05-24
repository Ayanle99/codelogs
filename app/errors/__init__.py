from flask import Blueprint

bp = Blueprint('errors', __name__, url_prefix='/errors', template_folder='templates')


from app.errors import handler