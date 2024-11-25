from app_center.authentication.logs import app_logs
from app_center import ERRORLOGDIR
from flask import render_template
from flask_login import login_required
import os

@app_logs.route('/lihat-logs')
@login_required
def lihat_logs():
  """ Routing Menampilkan Halaman Logs """
  filenames = os.listdir(ERRORLOGDIR)
  filenames.remove('.gitignore')
  filenames.sort(reverse=True)
  return render_template('logs/logs.html', files=filenames)

@app_logs.route('/open-logs/<path:filename>')
def open_logs(filename):
  """ ROUTING Fungsi Render isi logs kedalam HTML """
  with open(f"{ERRORLOGDIR}/{filename}") as f:
    lines = f.readlines()
  
  logs=''
  for row in lines:
    logs += f"<li>{row}</li>"
  return render_template('logs/render-logs.html', logs=logs, judul=filename)