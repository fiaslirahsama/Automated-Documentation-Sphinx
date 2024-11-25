from flask import Blueprint

app_master_init = Blueprint('master', __name__, static_folder='static', template_folder='templates')

from app_center.master import view_master