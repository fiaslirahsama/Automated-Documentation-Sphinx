import os, subprocess, shutil
from app_center import BASEDIR, db, app
from app_center.documentation import model as modoc
from app_center.authentication.logs import controller_logs
from datetime import datetime
from sqlalchemy import func, or_

MREPO = modoc.MasterRepository

def find_modules(base_dir, package_name):
    """
    Recursively find all modules and submodules in the specified directory.
    :param base_dir: Base directory to scan for modules.
    :param package_name: Package name to prefix module paths.
    :return: List of fully qualified module names.
    """
    modules = []
    for root, dirs, files in os.walk(base_dir):
        # Filter out directories starting with '__pycache__' or '.'
        dirs[:] = [d for d in dirs if not d.startswith('__') and not d.startswith('.')]

        # Compute the module path
        relative_path = os.path.relpath(root, base_dir).replace(os.sep, '.')
        module_base = f"{relative_path}" if relative_path != '.' else package_name
        # Add directories with __init__.py as modules
        if '__init__.py' in files:
          if module_base != package_name:
            modules.append(module_base)

    return modules

def createDummyConfig(app_dir):
  conf_dummy = f"""
import os
import pymysql
from sqlalchemy import create_engine
from sqlalchemy_utils import database_exists,create_database
from os.path import join, dirname, realpath

# # set the base directory
# basedir = os.path.abspath(os.path.dirname(__file__))

# set the base directory
BASEDIR = os.path.abspath(os.path.dirname(realpath(__file__)))

# Create the super class
class Config(object):
  SECRET_KEY = os.environ.get('SECRET_KEY')
  SQLALCHEMY_COMMIT_ON_TEARDOWN = True
  SQLALCHEMY_TRACK_MODIFICATIONS = False

# Create the development config
class DevelopmentConfig(Config):
  DEBUG = True
 
  HOST = str(os.environ.get("DB_HOST"))
  DATABASE = str(os.environ.get("DB_DATABASE"))
  USERNAME = str(os.environ.get("DB_USERNAME"))
  PASSWORD = str(os.environ.get("DB_PASSWORD"))
  
  DATABASE_FILE = 'mysql+pymysql://' + USERNAME + ':' + PASSWORD + '@' + HOST + '/' + DATABASE
  SQLALCHEMY_DATABASE_URI = DATABASE_FILE
  SQLALCHEMY_TRACK_MODIFICATIONS = False
  SQLALCHEMY_RECORD_QUERIES = True 
  
  """
  
  config_py = os.path.join(app_dir, 'config.py')
  config_py_temp = os.path.join(app_dir, 'config.py_temp')
  os.rename(config_py, config_py_temp)
  with open(config_py, "w+") as cfd:
    cfd.write(conf_dummy)

def deleteDummyConfig(app_dir):
  config_py = os.path.join(app_dir, 'config.py')
  config_py_temp = os.path.join(app_dir, 'config.py_temp')
  if os.path.exists(config_py) == True:
    os.remove(config_py)
  if os.path.exists(config_py) == False:
    os.rename(config_py_temp, config_py)
  
def initRSTFile(app_dir, source_dir, repo_name, app_center):
  modules = find_modules(app_dir, app_center)
  index_rst_path = os.path.join(source_dir, 'index.rst')
  with open(index_rst_path, 'w') as index_file:
            index_file.write(
                f"""
Welcome to {repo_name}'s documentation!
=======================================

.. toctree::
   :maxdepth: 2
   :caption: Contents:

"""
            )
            for module in modules:
                index_file.write(f"   {module}\n")

            index_file.write(
                """
Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`
"""
            )

def initConfigFile(app_dir, source_dir, repository):
  conf_path = os.path.join(source_dir, 'conf.py')
  lines = []
  with open(conf_path, 'r') as outr:
    lines = outr.readlines()
  
  with open(conf_path, 'w') as outw:
    for line in lines:
      if line.strip().startswith("html_theme = 'alabaster'"):
        outw.write("html_theme = 'sphinx_rtd_theme'\n")
      else:
        outw.write(line)
    outw.write(f"html_baseurl = '{repository}'\n")
    outw.write(f"\nimport os\nimport sys\nsys.path.insert(0, os.path.abspath('{app_dir}'))\n")

def generate_docs():
  """
  Generate Sphinx documentation by calling the Sphinx build command.
  """
  this_month = datetime.now().strftime("%m-%Y")
  reps = db.session.query(MREPO).with_entities(MREPO.repository_name, MREPO.app_center_name)\
                                .filter(or_(func.date_format(MREPO.last_date_documented,"%m-%Y")!=this_month,
                                            MREPO.last_date_documented==None)).all()
  
  for row in reps:
    dreps = row._asdict()
    APP_SOURCE_DIR = BASEDIR.replace("Automated-Documentation-Sphinx", dreps['repository_name']).replace("app_center","").replace('\\', '\\\\')
    TEMPLATE_DIR = os.path.join(os.path.join(BASEDIR, "templates\documentation"), dreps['repository_name'])
    SOURCE_DIR = os.path.join(TEMPLATE_DIR, 'source')
    BUILD_DIR = os.path.join(TEMPLATE_DIR, 'build')
    if os.path.exists(TEMPLATE_DIR) == True:
      shutil.rmtree(TEMPLATE_DIR, ignore_errors=True)
    if os.path.exists(TEMPLATE_DIR) == False:
      os.mkdir(TEMPLATE_DIR)
    try:
      subprocess.run(
        [
                'sphinx-quickstart',
                '--quiet',
                '--sep',
                '--project', dreps['repository_name'],
                '--author', 'Center 4.0',
                '--release', '1.0.0',
                '--ext-autodoc',
                '--ext-todo',
                '--ext-viewcode',
                '--makefile',
                '--batchfile',
                TEMPLATE_DIR,
            ],
            check=True
      )
      initConfigFile(APP_SOURCE_DIR, SOURCE_DIR, dreps['repository_name'])
      
      initRSTFile(APP_SOURCE_DIR, SOURCE_DIR, dreps['repository_name'], dreps['app_center_name'])
      
      createDummyConfig(APP_SOURCE_DIR)
      subprocess.run(
            ['sphinx-apidoc', '-o', SOURCE_DIR, APP_SOURCE_DIR],
            check=True
        )
      # # Run Sphinx build
      subprocess.run(
          ['sphinx-build', '-b', 'html', SOURCE_DIR, BUILD_DIR],
          check=True
      ) 
      deleteDummyConfig(APP_SOURCE_DIR)
      db.session.query(MREPO).filter(MREPO.repository_name==dreps['repository_name']).update({'last_date_documented':datetime.now()})
      db.session.commit()
      db.session.close()
      
      controller_logs.catat_log_error('generate_docs', f"Documentation {dreps['repository_name']} successfully generated.")
      print(f"Documentation {dreps['repository_name']} successfully generated.")
    except subprocess.CalledProcessError as e:
      controller_logs.catat_log_error('generate_docs', f"Error generating {dreps['repository_name']} documentation: {e}")
      print(f"Error generating {dreps['repository_name']} documentation: {e}")
    except Exception as e:
      controller_logs.catat_log_error('generate_docs', f"Unexpected error {dreps['repository_name']}: {e}")
      print(f"Unexpected error {dreps['repository_name']}: {e}")