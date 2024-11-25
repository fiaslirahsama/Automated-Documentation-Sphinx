from datetime import datetime
from app_center import db
from flask import abort
from flask_login import UserMixin, current_user
from flask_admin import expose, AdminIndexView
from flask_admin.contrib.sqla import ModelView 

def waktu_sekarang():
  waktu = datetime.now()
  return waktu

''' MODEL TABEL MASTER USER '''
class MasterUser(db.Model, UserMixin ):
  """ Model Tabel Database untuk menyimpan data USER """
  __tablename__ = 'user'
  id = db.Column(db.Integer, primary_key=True)
  nik = db.Column(db.String(10))
  nama = db.Column(db.String(50))
  password = db.Column(db.String(80))
  departemen = db.Column(db.String(50))
  golongan = db.Column(db.Integer)
  roles = db.Column(db.String(50))
  menu_akses = db.Column(db.Text)
  status_sso = db.Column(db.String(2), default=1)
  created_by = db.Column(db.String(100), default='SYSTEM')
  created_date = db.Column(db.DateTime, default=waktu_sekarang)
  status_aktif = db.Column(db.String(2), default=1)
  
''' VIEW ADMIN PAGE '''
class Controller(ModelView):
  """ Class untuk autentikasi halaman admin """
  def is_accessible(self):
    if current_user.is_god == True:
      return current_user.is_authenticated
    else:
      return abort(404)
    # return current_user.is_authenticated
  def not_auth(self):
    return 'Maaf Anda tidak Punya Akses untuk melihat ini !!!'
  
''' DASHBOARD ADMIN '''
class DashboardView(AdminIndexView):
    """ Class untuk render dashboard admin """
    def is_visible(self):
        # This view won't appear in the menu structure
        return False

    # @expose('/')
    # def index(self):

    #     return self.render(
    #         'admin/dashboard.html',
    #     )