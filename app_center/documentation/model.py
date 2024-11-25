from datetime import datetime
from app_center import db

def waktu_sekarang():
  waktu = datetime.now()
  return waktu

''' MODEL TABEL MASTER USER '''
class MasterRepository(db.Model):
  """ Master Repository name """
  __tablename__ = 'm_repository'
  id = db.Column(db.Integer, primary_key=True)
  repository_name = db.Column(db.String(255), index=True)
  app_center_name = db.Column(db.String(255))
  icon_file = db.Column(db.Text)
  last_date_documented = db.Column(db.DateTime, default=None)

  