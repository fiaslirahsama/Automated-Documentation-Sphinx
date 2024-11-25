from flask.helpers import flash
from app_center.authentication.login import app_login_init, controller, model
from flask import render_template, redirect, url_for, request
from flask_login import login_user, login_required, current_user, logout_user
from flask_minify import Minify, decorators as minify_decorators

''' DEFAULT URL '''
@app_login_init.route('/')
# @minify_decorators.minify(html=True, js=True, cssless=True)
def route_default():
  """ Routing default url """
  return redirect(url_for('login.login'))

''' VIEW LOGIN '''
@app_login_init.route('/login')
# @minify_decorators.minify(html=True, js=True, cssless=True)
def login():
  """ Routing halaman login """
  if(current_user.is_authenticated == True):
    return redirect(url_for('home.home'))
  else:
    return render_template('accounts/login.html')

''' PROSES LOGIN '''
# ----------------------- LOGIN -----------------------------------------#
@app_login_init.route('/login', methods=['POST'])
# @minify_decorators.minify(html=True, js=True, cssless=True)
def login_post():
  """ 
  Routing untuk memproses session login.
  Apabila berhasil login akan langsung dialihkan ke halaman home 
  """
  render_self = controller.loginPost()
  if render_self == True :
    return render_template('accounts/login.html') 
  else:
    return redirect(url_for('home.home'))


''' PROSES LOGOUT '''
# ----------------------- LOGOUT -----------------------------------------#
@app_login_init.route('/logout')
# @minify_decorators.minify(html=True, js=True, cssless=True)
@login_required
def logout():
  """ 
  Routing untuk memproses session logout.
  Apabila berhasil logout akan langsung dialihkan ke halaman login 
  """
  logout_user()
  return redirect(url_for('login.logout'))

# # REGISTER
# @app_login_init.route('/register', methods=['POST', 'GET'])
# def register():
#   msg = ''
#   nik = request.form.get('nik_daftar')
#   nama = request.form.get('nama_daftar')
#   password = request.form.get('password_daftar')
  
#   user = model.User.query.filter_by(nik=nik).first()
  
#   if user:
#     return 'user sudah ada'
  
#   # new_user = model.User(nik=nik, nama=nama, password=generate_password_hash(password, method='sha256'))
#   new_user = model.User(nik=nik, nama=nama, password=password)
  
#   # add the new user to the database
#   db.session.add(new_user)
#   db.session.commit() 
  
#   msg='Berhasil Mendaftar'
#   return render_template('login/login.html', msg=msg)



# ----------------------- ERORR -----------------------------------------#
''' ERROR HANDLING 403 '''
@app_login_init.errorhandler(403)
def access_forbidden(error):
    return render_template('home/page-403.html'), 403

''' ERROR HANDLING 404 '''
@app_login_init.errorhandler(404)
def not_found_error(error):
    return render_template('home/page-404.html'), 404


''' ERROR HANDLING 500 '''
@app_login_init.errorhandler(500)
def internal_error(error):
    return render_template('home/page-500.html'), 500