import os, pymysql
from sqlalchemy import create_engine
from sqlalchemy_utils import database_exists,create_database
# linux to windows

# set the base directory
BASEDIR = os.path.abspath(os.path.dirname(__file__))

# Set Create Folder
def createFolder(PATH):
    folderPath = os.path.join(BASEDIR, PATH)
    os.makedirs(folderPath)

# Auto Create Name DB
def validateDatabase(DATABASE_FILE, DB_NAME):
    engine = create_engine(DATABASE_FILE)
    if not database_exists(engine.url): # Checks for the first time  
        create_database(engine.url)     # Create new DB    
        print(f"{DB_NAME} Database Created") # Verifies if database is there or not.
    else:
        print(f"Database {DB_NAME} Running")

# Create the super class
class Config(object):
  SECRET_KEY = os.environ.get('SECRET_KEY')
  
  
# Create the development config
class DevelopmentConfig(Config):
  DEBUG = True

######################################### LOGS ##############################################   
  LOGS_FOLDER = "./app_center/static/logs/"
  CEK_LOGS_FOLDER = os.path.exists(LOGS_FOLDER)
  GITIGNORE_PATH = os.path.join(LOGS_FOLDER, '.gitignore')
  CEK_GITIGNORE = os.path.exists(GITIGNORE_PATH)

  if not CEK_LOGS_FOLDER:
    createFolder(LOGS_FOLDER)
    print(f"Folder Logs Telah Dibuat")
  
  if not CEK_GITIGNORE and CEK_LOGS_FOLDER == True:
    with open(GITIGNORE_PATH, 'w+') as f:
      f.write("*\n*/\n!.gitignore")
    print("File Gitignore untuk logs telah dibuat")

#############################################################################################
######################################### FILES #############################################
  FILES_FOLDER = "./app_center/static/files/"
  CEK_FILES_FOLDER = os.path.exists(FILES_FOLDER)
  GITIGNORE_PATH = os.path.join(FILES_FOLDER, ".gitignore")
  CEK_GITIGNORE = os.path.exists(GITIGNORE_PATH)
  if not CEK_FILES_FOLDER:
    createFolder(FILES_FOLDER)
    print(f"Folder Files Telah Dibuat")
  
  if not CEK_GITIGNORE and CEK_FILES_FOLDER == True:
    with open(GITIGNORE_PATH, 'w+') as f:
      f.write("*\n*/\n!.gitignore")
    print("File Gitignore untuk files telah dibuat")

#############################################################################################
  HOST = str(os.environ.get("DB_HOST"))
  DATABASE = str(os.environ.get("DB_DATABASE"))
  USERNAME = str(os.environ.get("DB_USERNAME"))
  PASSWORD = str(os.environ.get("DB_PASSWORD"))
  
  DATABASE_FILE = f'mysql+pymysql://{USERNAME}:{PASSWORD}@{HOST}/{DATABASE}'

  validateDatabase(DATABASE_FILE, DATABASE)
  SQLALCHEMY_DATABASE_URI = DATABASE_FILE
  SQLALCHEMY_TRACK_MODIFICATIONS = False
  SQLALCHEMY_RECORD_QUERIES = True 
  
