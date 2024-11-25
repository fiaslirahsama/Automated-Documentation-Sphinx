from flask import Blueprint

app_documentation_init = Blueprint('documentation', __name__, static_folder='static', template_folder='templates')

from app_center.documentation import view