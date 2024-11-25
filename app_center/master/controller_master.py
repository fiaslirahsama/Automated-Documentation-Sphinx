from app_center import db, FILEDIR
from app_center.documentation import model as modoc
from app_center.master import model_master
from flask import jsonify, request, flash, render_template, redirect, url_for
from werkzeug.utils import secure_filename
from datetime import datetime, timedelta
from dateutil.relativedelta import relativedelta
from flask_login import current_user
from sqlalchemy import and_, or_, func, cast, DATE, case
from app_center.modules import controller_module
import pandas as pd, json, os


''' DEFINE INITIAL MODEL MASTER '''

MREPO = modoc.MasterRepository


def getMasterRepository():
  data = db.session.query(MREPO).all()
  return data

def fetchMasterRepository():
  datatable = controller_module.Datatable(request.form)
  search_value = datatable.get_search_value()
  sort_col_name = ['id', 'repository_name', 'app_center_name', 'icon_file', 'last_date_documented']
  sort_obj = {'id':MREPO.id,
              'repository_name':MREPO.repository_name,
              'app_center_name':MREPO.app_center_name,
              'icon_file':MREPO.icon_file,
              'last_date_documented':MREPO.last_date_documented}
  order = datatable.get_order(sort_col_name=sort_col_name, sort_obj=sort_obj)
  order.append(MREPO.id)
  
  jumlah_data_full = db.session.query(MREPO).count()
  query_filtered = db.session.query(MREPO).with_entities(MREPO.id,
                                                          MREPO.repository_name,
                                                          MREPO.app_center_name,
                                                          MREPO.icon_file,
                                                          func.date_format(MREPO.last_date_documented, "%d-%m-%Y").label("last_date_documented"))\
                                            .filter(or_(func.date_format(MREPO.last_date_documented, "%d-%m-%Y").like(search_value),
                                                        MREPO.repository_name.like(search_value),
                                                        MREPO.app_center_name.like(search_value),
                                                        ))\
                                            .order_by(*order)
  data_json = datatable.get_data_json_with_entities(query_filtered)
  response = datatable.get_response(jumlah_data_full=jumlah_data_full, data_json=data_json)
  return jsonify(response)

def addMasterRepository():
  data_insert = {}
  for row in request.form.keys():
    if row not in ['icon_file', 'mode']:
      data_insert[row] = request.form.get(row)
  cek_data = db.session.query(MREPO).filter(MREPO.repository_name==data_insert['repository_name']).count()
  if cek_data > 0:
    return jsonify({'status':'error', 'message': f"Repository {data_insert['repository_name']} Sudah Ada!"})
  addin = MREPO(**data_insert)
  db.session.add(addin)
  db.session.commit()
  
  files = request.files.get('icon_file')
  formattins = secure_filename(files.filename).split(".")[-1]
  if formattins not in [None, ''] and formattins.lower() in ['jpg', 'jpeg', 'png']:
    filename = secure_filename(f"{data_insert['repository_name']}.{formattins.lower()}")
    file_folder = os.path.join(FILEDIR, filename)
    files.save(file_folder)
    db.session.query(MREPO).filter(MREPO.id==addin.id).update({'icon_file':filename})
    db.session.commit()
  
  db.session.close()
  return redirect(url_for('master.m_repository'))

def editMasterRepository():
  data_insert = {}
  for row in request.form.keys():
    if row not in ['icon_file', 'mode']:
      data_insert[row] = request.form.get(row)
  
  db.session.query(MREPO).filter(MREPO.id==data_insert['id']).update(data_insert)
  db.session.commit()    
      
  files = request.files.get('icon_file')
  formattins = secure_filename(files.filename).split(".")[-1]
  if formattins not in [None, ''] and formattins.lower() in ['jpg', 'jpeg', 'png']:
    filename = secure_filename(f"{data_insert['repository_name']}.{formattins.lower()}")
    file_folder = os.path.join(FILEDIR, filename)
    files.save(file_folder)
    db.session.query(MREPO).filter(MREPO.id==data_insert['id']).update({'icon_file':filename})
    db.session.commit()
  
  db.session.close()
  return redirect(url_for('master.m_repository'))
  
def deleteMasterRepository():
  id_delete = request.form.get('id')
  db.session.query(MREPO).filter(MREPO.id==id_delete).delete()
  db.session.commit()
  db.session.close()
  return jsonify({'status':'ok', 'message':'Berhasil Delete Repository'})