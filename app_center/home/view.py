from flask.helpers import flash
from flask import render_template, redirect, url_for, request
from app_center.home import app_home_init, controller
from app_center.documentation import model
from werkzeug.security import generate_password_hash, check_password_hash
from app_center import db, ERRORLOGDIR
from flask_login import login_user, login_required, current_user, logout_user
from datetime import datetime, timedelta
import os

# '''VIEW HOME'''
# @app_home_init.route('/home')
# @login_required
# def home():
#   """ Routing Menampilkan Halaman Home """
#   # return 'home'
#   return render_template('home/home.html')

'''VIEW OVERVIEW DASHBOARD'''
@app_home_init.route('/home', methods=['GET', 'POST'])
@login_required
def home():
  """ Routing Menampilkan Halaman Overview Dashboard """
  rm = True if request.method=='POST' else False
  mode = request.form.get('mode')
  repository = [{'repository':x.repository_name, 'icon_file':x.icon_file} for x in db.session.query(model.MasterRepository.repository_name, model.MasterRepository.icon_file).filter(model.MasterRepository.last_date_documented!=None).all()]
  return render_template('home/home.html', root='', repository=repository, title='Home')