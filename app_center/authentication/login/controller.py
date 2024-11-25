from flask.helpers import flash
from app_center.authentication.login import app_login_init, controller, model
from flask import render_template, redirect, url_for, request
from werkzeug.security import generate_password_hash, check_password_hash
from app_center import db
from flask_login import login_user, login_required, current_user, logout_user
from flask_minify import Minify, decorators as minify_decorators
from datetime import datetime

""" INIT MODEL """
USER = model.MasterUser


''' SUBMIT LOGIN '''
def loginPost():
  """ Fungsi untuk memproses session saat login.
      Username dan password akan dicek terlebih dahulu sebelum masuk ke aplikasi. """
  nik = request.form.get('nik')
  password = request.form.get('password')
  user_login = db.session.query(USER).filter(USER.nik==nik, USER.password==password, USER.status_aktif=='1').first()
  if user_login:
    login_user(user_login)
    flash("Berhasil Login!", 'success')
    return False
  else:
    flash("Password Salah!", "warning")
    return True
        
        
