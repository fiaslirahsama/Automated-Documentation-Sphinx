from flask import views, jsonify, request
from flask.typing import ResponseReturnValue
from sqlalchemy import create_engine, text
import io, os, time, subprocess, platform, threading
from Crypto.Cipher import AES
from Crypto.Util import Padding
import io, os, time, logging, subprocess, platform, base64



progress_object = {}

########################################### MIGRATE UPGRADE RESET ALEMBIK ####################################
def configurationAlembic():
  """
  CONFIGURATION ALEMBIC.INI BIAR KEUAR LOGNYA SAAT MIGRATE UPGRADE PAKE ROUTINGAN
  """
  string_config_alembic = """ 
    # A generic, single database configuration.

    [alembic]
    # template used to generate migration files
    # file_template = %%(rev)s_%%(slug)s

    # set to 'true' to run the environment during
    # the 'revision' command, regardless of autogenerate
    # revision_environment = false


    # Logging configuration
    [loggers]
    keys = root,sqlalchemy,alembic,flask_migrate

    [handlers]
    keys = console,flask

    [formatters]
    keys = generic

    [logger_root]
    level = WARN
    handlers = console,flask
    qualname =

    [logger_sqlalchemy]
    level = WARN
    handlers = flask
    qualname = sqlalchemy.engine

    [logger_alembic]
    level = INFO
    handlers = flask
    qualname = alembic

    [logger_flask_migrate]
    level = INFO
    handlers = flask
    qualname = flask_migrate

    [handler_console]
    class = StreamHandler
    args = (sys.stderr,)
    level = NOTSET
    formatter = generic

    [handler_flask]
    class = FileHandler
    level = DEBUG
    formatter= generic
    args=('migrations/log_migrate_upgrade.log', 'w')

    [formatter_generic]
    format = %(levelname)-5.5s [%(name)s] %(message)s
    datefmt = %H:%M:%S
  """
  with open('migrations/alembic.ini', 'w+') as f:
    f.write(string_config_alembic)

class DBMigrate(views.View):
  """Migrate DB pakai routingan
  """
  methods = ['GET']
  def dispatch_request(self):
    if os.path.exists('migrations/log_migrate_upgrade.log') == False:
      configurationAlembic()
    subprocess.run(["flask",'db','migrate'])
    with open('migrations/log_migrate_upgrade.log') as f:
      lines = f.readlines()
    logs = ''
    for row in lines:
      logs += f"<li>{row}</li>"
    return logs

class DBUpgrade(views.View):
  """Upgrade DB pakai routingan
  """
  methods = ['GET']
  def dispatch_request(self):
    if os.path.exists('migrations/log_migrate_upgrade.log') == False:
      configurationAlembic()
    subprocess.run(["flask",'db','upgrade'])
    with open('migrations/log_migrate_upgrade.log') as f:
      lines = f.readlines()
    logs = ''
    for row in lines:
      logs += f"<li>{row}</li>"
    return logs
  
class DBResetAlembic(views.View):
  """Modul untuk reset alembic apabila stuck gabisa migrate

  Args:
      VERSIONDIR = lokasi folder version
      DATABASE_FILE = alamat databasenya

  Returns:
      logging alembic
  """
  methods = ['GET']
  def dispatch_request(self):
    VERSIONDIR = './migrations/versions'
    DATABASE_FILE = f"mysql+pymysql://{os.environ['DB_USERNAME']}:{os.environ['DB_PASSWORD']}@{os.environ['DB_HOST']}/{os.environ['DB_DATABASE']}"
    engine = create_engine(DATABASE_FILE)
    with engine.connect() as conn:
      stmt = text(""" TRUNCATE alembic_version """)
      conn.execute(stmt)
    html = "<b><h1>OKESIP Tabel alembic_version Empty Complete</h1></b><br>"
    filenames = os.listdir(VERSIONDIR)
    filenames.remove('.gitignore')
    filenames.remove('__pycache__')
    html += '<ul>'
    for fn in filenames:
      os.remove(os.path.join(VERSIONDIR, fn))
      html += f"<li><h3>File {fn} Removed Complete</h3></li>"
    html += '</ul>'
    return html

############################################ GIT PULL DAN RESTART APP #############################################
class GitPull(views.View):
  """Modul untuk melakukan gitpull server dengan routingan

  Args:
      nama_repo = Masukkan nama repo yang sedang digunakan oleh app
      username = username github
      sshkey = ssh key github untuk pulling

  Returns:
      daftar apa saja yang sedang di pull dan button untuk restart app
  """
  methods = ["GET"]
  def dispatch_request(self):
    try:
      nama_repo = 'Power-Monitoring'
      username = 'itqms6'
      sshkey = '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'
      subprocess.run(['git','remote','set-url', 'origin', f'https://{username}:{sshkey}@github.com/PT-Untung-Bersama-Sejahtera/{nama_repo}.git'])
      subprocess.run(['git', 'config', 'credential.helper', 'store'])
      subprocess.run(['git', 'config', '--global', 'credential.helper', 'store'])
      process = subprocess.Popen(["git", "pull"], stdin=subprocess.PIPE, stdout=subprocess.PIPE)
      buffer_log = []
      html = '<ul>'
      with process.stdout:
        for line in iter(process.stdout.readline, b''):
          buffer_log.append(line)
      for text in buffer_log:
        html += f"<li> {text.decode('utf-8')} </li>"
      html += '</ul>'
      html += '<br>'
      html += "<a href='systemctl-restart'><h2>Restart APP (KHUSUS SERVER)</h2></a>"
      if buffer_log == []:
        return 'Terjadi Kesalahan, Silahkan Periksa Koneksi'
      return html
    except Exception as e:
      return e

class SystemCTLRestart(views.View):
  """Modul Routingan untuk merestart service flask APP pada server ubuntu

  Args:
      operating_sistem = Jenis OS yang dipakai server 
      flask_app_service_name = Nama service flask APP

  Returns:
      restart service
  """
  methods = ["GET"]
  def dispatch_request(self):
    try:
      operating_sistem = platform.system()
      flask_app_service_name = "flask-busduct"
      if operating_sistem == 'Windows':
        return 'OS mu windows raiso'
      process = subprocess.Popen(["sudo", "-S", "systemctl", "restart", flask_app_service_name], stdin=subprocess.PIPE, stdout=subprocess.PIPE, universal_newlines=True)
      process.communicate('123456'+'\n')[1]
      return f'{flask_app_service_name} restarted, OS : {operating_sistem}'
    except Exception as e:
      return e

class JournalCTL(views.View):
  """Modul Routingan Untuk Liat Logging Journal CTL"""
  methods = ['GET']
  def dispatch_request(self):
    try:
      operating_sistem = platform.system()
      flask_app_service_name = "flask-busduct"
      if operating_sistem == 'Windows':
        return 'OS mu Windows Raiso'
      process = subprocess.check_output(["journalctl", "-u", flask_app_service_name, "--since", "1800 seconds ago", "--no-pager"])
      buffer_log = process.split(b'\n')
      buffer_log.pop(0)
      html = f"<h3>-- Log Journal Sejak 30 Menit Lalu --</h3>"
      html += '<ul>'
      for text in reversed(buffer_log):
        html += f"<li> {text.decode('utf-8')} </li>"
      html += '</ul>'
      html += '<br>'
      return html
    except Exception as e:
      return f"{e}"

############################################ PROGRESS BAR #########################################
class GetProgress(views.View):
  """ routing get-progress untuk frontend ambil progress dari backend 
  
      Harap masukkan code dibawah pada __init__.py nya app_center :
      from app_center.modules.controller_module import GetProgress
      app.add_url_rule('/get-progress', view_func=GetProgress.as_view("get_progress"), methods=['GET', 'POST'])
  """
  methods = ["GET", "POST"]
  def dispatch_request(self):
    random_progress_id = request.form.get('random_progress_id')
    try:
      progress = progress_object[random_progress_id]
    except Exception as e:
      return jsonify({'Progress': [0, "Loading..."]})
    if progress == 100 or progress == '100':
      progress = progress_object.pop(random_progress_id)
    return jsonify({'Progress': progress})


class ProgressBar:
  """
  Modul Progress Bar
  
  """
  def __init__(self, random_progress_id:str):
    self.random_progress_id = random_progress_id
  
  def start(self, persen:int=0, message:str="Inisialisasi..."):
    progress_object[self.random_progress_id] = [persen, message]
    time.sleep(0.2)
  
  def update(self, persen:int, message:str):
    progress_object[self.random_progress_id] = [persen, message]
    time.sleep(0.2)
    
  def update_no_sleep(self, persen:int, message:str):
    progress_object[self.random_progress_id] = [persen, message]
    
  def error(self, persen:int=100, message:str="Mengembalikan Keadaan Semula..."):
    progress_object[self.random_progress_id] = [persen, message]
    time.sleep(1)
  
  def finish(self, persen:int=100, message:str="Selesai."):
    progress_object[self.random_progress_id] = [persen, message]
    time.sleep(1)

############################################ DATATABLE SERVERSIDE #########################################

class Datatable:
  def __init__(self, request_form):
    self.draw = request_form.get('draw')
    self.row_start = int(request_form.get('start'))
    self.row_per_page = int(request_form.get('length'))
    self.column_index = request_form.get('order[0][column]')
    self.column_name = request_form.get(f'columns[{self.column_index}][data]')
    self.column_sort_order = request_form.get('order[0][dir]')
    self.search_value = request_form.get('search[value]')
    self.jumlah_data_filtered = 0
    self.data_json = []
    
  def get_search_value(self):
    return f"%{self.search_value}%"
    
  def get_order(self, sort_col_name:list=[], sort_obj:dict={}, default_order:int=0):
    order = []
    self.column_name = sort_col_name[default_order] if self.column_name not in sort_col_name else self.column_name
    col = sort_obj[self.column_name].desc() if self.column_sort_order == 'desc' else sort_obj[self.column_name]
    order.append(col)
    return order
  
  def get_data_json_with_entities(self, query_filtered):
    self.jumlah_data_filtered = query_filtered.count()
    data_filtered = query_filtered.slice(self.row_start, self.row_start+self.row_per_page).all()
    self.data_json.clear()
    self.data_json.extend([x._asdict() for x in data_filtered])
    return self.data_json

  def get_data_json_with_entities_list_iter(self, query_filtered):
    self.jumlah_data_filtered = query_filtered.count()
    data_filtered = query_filtered.all()
    self.data_json.clear()
    self.data_json.extend([x._asdict() for x in data_filtered[self.row_start:self.row_start+self.row_per_page]])
    return self.data_json
  
  def get_data_json_without_with_entities(self, query_filtered):
    self.jumlah_data_filtered = query_filtered.count()
    data_filtered = query_filtered.slice(self.row_start, self.row_start+self.row_per_page).all()
    self.data_json.clear()
    menjes = []
    for x in data_filtered:
      xdict = x.__dict__
      del xdict['_sa_instance_state']
      menjes.append(xdict)
    self.data_json.extend(menjes)
    return self.data_json
  
  def get_response(self, jumlah_data_full:int=0, data_json:list=[]):
    if jumlah_data_full == 0:
      jumlah_data_full = self.jumlah_data_filtered
    if data_json == []:
      data_json = self.data_json

    return {
      'draw': self.draw,
      'iTotalRecords': jumlah_data_full,
      'iTotalDisplayRecords': self.jumlah_data_filtered,
      'aaData': data_json
    }
   
######################################################################################################
########################################### AES ENCRYPT ##############################################
######################################################################################################

class AES128:
  def __init__(self, key, iv, plaintext:str):
    self.key = key
    self.iv = iv
    self.plaintext = plaintext
    self.block_size = AES.block_size
    
  def encryptCBC(self):
    if type(self.key) == str:
      self.key = self.key.encode()
    if type(self.iv) == str:
      self.iv = self.iv.encode()
    if type(self.plaintext) != str:
      raise TypeError("PLAINTEXT HARUS STRING !!!")

    msg = Padding.pad(self.plaintext.encode(), AES.block_size)
    cipher = AES.new(self.key, AES.MODE_CBC, self.iv)
    cipher_text = cipher.encrypt(msg)
    output = base64.b64encode(cipher_text).decode('utf-8')
    return output
  
  def decryptCBC(self):
    if type(self.key) == str:
      self.key = self.key.encode()
    if type(self.iv) == str:
      self.iv = self.iv.encode()
    if type(self.plaintext) != str:
      raise TypeError("PLAINTEXT HARUS STRING !!!")
    
    msg = base64.b64decode(self.plaintext)
    decipher = AES.new(self.key, AES.MODE_CBC, self.iv)
    decipher_text = decipher.decrypt(msg)
    output = Padding.unpad(decipher_text, AES.block_size).decode('utf-8')
    return output
  
  ################################################### SET INTERVAL PYTHON #############################################
  
class setInterval:
  """
  Modul Untuk Melakukan Pengulangan asynchronus secara interval
  """

  def __init__(self, run_function, seconds, args=(), kwargs={}):
    self.run_function = run_function
    self.seconds = seconds
    self.stop_event = threading.Event()
    self.args = args
    self.kwargs = kwargs
    thread = threading.Thread(target=self.__setInterval)
    thread.start()
    
  def __setInterval(self):
    next_time = time.time()+self.seconds
    while not self.stop_event.wait(next_time-time.time()):
      next_time+=self.seconds
      self.run_function(*self.args, **self.kwargs)
      
  def cancel(self):
    self.stop_event.set()
    
  # def return_function(self):
  #   print("cuoooooo")
  #   def func_wrapper():
  #     self.return_function(self)
  #     self.run_function(*self.args, **self.kwargs)
  #   t = threading.Timer(self.seconds, func_wrapper)
  #   t.start()
  #   return t

# def setInterval2(func, sec):
#     def func_wrapper():
#         setInterval2(func, sec)
#         func()
#     t = threading.Timer(sec, func_wrapper)
#     t.start()
#     return t