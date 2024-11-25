from flask import Blueprint

app_logs = Blueprint('app_logs', __name__, template_folder='templates', static_folder='static')

from app_center.authentication.logs import view_logs