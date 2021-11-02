from flask import Flask, jsonify, make_response, request, render_template, redirect, send_from_directory, url_for, Response
from flask_swagger_ui import get_swaggerui_blueprint
from os import path
import json

from flask_apscheduler import APScheduler

SWAGGER_URL = '/swagger'
#API_URL = '/static/swagger5.yaml'
API_URL = 'static/swagger_docs.yaml'

swaggerui_blueprint = get_swaggerui_blueprint(
    SWAGGER_URL,
    API_URL,
    config={
        'app_name': "Carbon API testing"
    }
)

"""
DEFINING CONSTANTS
"""


"""
Changing design pattern from monolith to application factory
By returning an instance of the app instead of a monolith, it 
separates the dependency of app configuration and the app itself.

For testing and maintainability, we could experiment with diff
environments, URL routing, etc. by just specifying which config
file to use. 

Default, it'll create the app as it did in the first iteration.
"""


def create_flask_app(config=None):
    app = Flask(__name__)
    if config:
        app.config.from_pyfile(config)
    else:
        current_directory = path.dirname(path.realpath('__file__'))
        upload_directory = path.join(current_directory, 'uploads')
        print(upload_directory)
        app.config['UPLOAD_FOLDER'] = upload_directory
        app.config['ROOT_DIR'] = current_directory
    app.register_blueprint(swaggerui_blueprint, url_prefix=SWAGGER_URL)
    scheduler = APScheduler()
    scheduler.init_app(app)
    scheduler.start()
    app.config['SCHEDULER'] = scheduler
    return app
