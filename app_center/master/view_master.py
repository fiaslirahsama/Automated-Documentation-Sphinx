from flask.helpers import flash
from flask import jsonify, render_template, redirect, url_for, request
from app_center.master import app_master_init, controller_master
from werkzeug.security import generate_password_hash, check_password_hash
from app_center import db
from flask_login import login_user, login_required, current_user, logout_user
from datetime import datetime

@app_master_init.route('/m-repository', methods=['GET', 'POST'])
@login_required
def m_repository():
  rm = True if request.method == 'POST' else False
  mode = request.form.get('mode')
  if rm and mode == 'datatable':
    return controller_master.fetchMasterRepository()
  elif rm and mode == 'add':
    return controller_master.addMasterRepository()
  elif rm and mode == 'edit':
    return controller_master.editMasterRepository()
  elif rm and mode == 'delete':
    return controller_master.deleteMasterRepository()
  return render_template('master/m-repository.html', root='Repository', title='Repository')
