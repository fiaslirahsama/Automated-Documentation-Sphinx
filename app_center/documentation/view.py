from app_center.documentation import controller, app_documentation_init
from flask import render_template, redirect, url_for, request, send_from_directory, jsonify, Flask, send_file
from flask_login import login_user, login_required, current_user, logout_user
from app_center import BASEDIR, app
import os, shutil

TEMPLATEDIR = os.path.join(BASEDIR, 'templates')
STATICDIR = os.path.join(BASEDIR, 'static')

# @app_documentation_init.route('/documentation/_static/css/fonts/<file>')
# @login_required
# def docs_static_css_fonts(file):
#   print(file)
#   return send_from_directory(os.path.join(STATICDIR, 'static_sphinx/css/fonts'), file)

# @app_documentation_init.route('/documentation/_static/css/<file>')
# @login_required
# def docs_static_css(file):
#   print(file)
#   return send_from_directory(os.path.join(STATICDIR, 'static_sphinx/css'), file)

# @app_documentation_init.route('/documentation/_static/js/<file>')
# @login_required
# def docs_static_js(file):
#   print(file)
#   return send_from_directory(os.path.join(STATICDIR, 'static_sphinx/js'), file)

# @app_documentation_init.route('/documentation/_static/<file>')
# @login_required
# def docs_static(file):
#   print(file)
#   return send_from_directory(os.path.join(STATICDIR, 'static_sphinx'), file)

# @app_documentation_init.route('/documentation/<repository>')
@app_documentation_init.route('/zip-file', methods=['POST'])
@login_required
def documentation():
  try:
    repository = request.form.get('repository')
    foldir = os.path.join(TEMPLATEDIR, f'documentation/{repository}')
    zipfile = shutil.make_archive(repository, 'zip', foldir, 'build')
    return send_file(zipfile)
    # return render_template(f'documentation/{repository}/build/index.html')
  except Exception as e:
    return jsonify({"error": str(e)}), 500