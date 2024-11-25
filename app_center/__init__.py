from flask import Flask, session, g
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from config import DevelopmentConfig
from flask_login import LoginManager, current_user
from flask_admin import Admin
from flask_admin.contrib.sqla import ModelView
from flask_admin.menu import MenuLink
from datetime import timedelta, datetime
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.jobstores.sqlalchemy import SQLAlchemyJobStore
from pytz import timezone
from flask_mysqldb import MySQL
import MySQLdb.cursors, os

HOST = str(os.environ.get("DB_HOST"))
DATABASE = str(os.environ.get("DB_DATABASE"))
USERNAME = str(os.environ.get("DB_USERNAME"))
PASSWORD = str(os.environ.get("DB_PASSWORD"))

DATABASE_FILE = f'mysql+pymysql://{USERNAME}:{PASSWORD}@{HOST}/{DATABASE}'

BASEDIR = os.path.abspath(os.path.dirname(os.path.realpath(__file__)))
ERRORLOGDIR = os.path.join(BASEDIR,'./static/logs') 
FILEDIR = os.path.join(BASEDIR, './static/files')

BLUEPRINTER = {}

scheduler = BackgroundScheduler(timezone=timezone('Asia/Jakarta'),
                                jobstores={'default':SQLAlchemyJobStore(url=DATABASE_FILE, tablename='apscheduler_jobs')},)

db = SQLAlchemy()
migrate = Migrate()
mysql = MySQL()
curMysql = MySQLdb.cursors.DictCursor
app = Flask(__name__)

def center_app(config=DevelopmentConfig):  
  app.config.from_object(config)
  app.config["DEBUG"] = True   
  
  @app.after_request
  def after_request(response):
      response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate, public, max-age=0"
      response.headers["Expires"] = 0
      response.headers["Pragma"] = "no-cache"
      return response
    
  @app.before_request
  def make_session_permanent():
    session.permanent = True
    app.permanent_session_lifetime = timedelta(minutes=45)
    session.modified = True
    g.user = current_user

  app.config['MYSQL_HOST']=os.environ.get('DB_HOST')  # dikoneksikan dengan database
  app.config['MYSQL_USER']=os.environ.get('DB_USERNAME')
  app.config['MYSQL_PASSWORD']=os.environ.get('DB_PASSWORD')
  app.config['MYSQL_DB']=os.environ.get('DB_DATABASE')
  app.config['SESSION_COOKIE_NAME'] = 'Automated-Documentation-Sphinx'
  # initialize extension instances
  mysql.init_app(app)
  mysql.app = app
    
  # initialize extension instances
  db.init_app(app)
  db.app = app
  
  # initialize extension instances
  migrate.init_app(app, db)
  migrate.app = app 
  
  from app_center.documentation import controller as condo
  if os.environ.get('FLASK_ENV') == 'Production':
    scheduler.add_job(condo.generate_docs, trigger='date', run_date=datetime.now(), id='generate_docs', replace_existing=True)  # Adjust interval as needed
    scheduler.add_job(condo.generate_docs, trigger='cron', day_of_week='mon-sun', hour=0, minute=6, second=0, id='generate_docs_daily', replace_existing=True)
    scheduler.start()
  
  login_manager = LoginManager()
  login_manager.init_app(app)  
  login_manager.login_view = 'login.login'
  
  from app_center.authentication.login import model
  @login_manager.user_loader
  def load_user(user_id):
    # since the user_id is just the primary key of our user table, use it in the query for the user
    user = model.MasterUser.query.get(int(user_id))
    if user == None:
      return user
    user.env = os.environ.get('FLASK_ENV')
    return user
  
  ''' LOGIN '''
  from app_center.authentication.login import app_login_init as login
  app.register_blueprint(login)
  from app_center.authentication.logs import app_logs as logs
  app.register_blueprint(logs)
  ''' DOCUMENTATION '''
  from app_center.documentation import app_documentation_init as docu
  app.register_blueprint(docu)
  ''' MASTER '''
  from app_center.master import app_master_init as master
  app.register_blueprint(master)
  from app_center.home import app_home_init as home
  app.register_blueprint(home)
  
  from app_center.modules import controller_module as cmod
  app.add_url_rule('/get-progress', view_func=cmod.GetProgress.as_view("get_progress"), methods=['GET', 'POST'])
  app.add_url_rule('/flask-db-migrate', view_func=cmod.DBMigrate.as_view('db_migrate'), methods=['GET'])
  app.add_url_rule('/flask-db-upgrade', view_func=cmod.DBUpgrade.as_view('db_upgrade'), methods=['GET'])
  app.add_url_rule('/flask-db-reset', view_func=cmod.DBResetAlembic.as_view('db_reset'), methods=['GET'])
  app.add_url_rule('/git-pull', view_func=cmod.GitPull.as_view('git_pull'), methods=['GET'])
  app.add_url_rule('/systemctl-restart', view_func=cmod.SystemCTLRestart.as_view('systemctl_restart'), methods=['GET'])
  app.add_url_rule('/journalctl', view_func=cmod.JournalCTL.as_view('journalctl'), methods=['GET'])
  
  return app
