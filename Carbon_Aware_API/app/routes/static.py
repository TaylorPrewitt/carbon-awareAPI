#app/routes/static

from flask import Blueprint, redirect
from flask.helpers import url_for
from flask.templating import render_template

"""
Meant to serve to hold static pages such as documentation or the start page
"""

static_bp = Blueprint('static_bp', __name__)

@static_bp.route("/home")
def home():

    return render_template('start.html')

@static_bp.route("/")
def start():
    return redirect(url_for('static_bp.home'))

@static_bp.route('/docs_page')
def docs_page():
    return render_template('appendix.html')

@static_bp.route('/deck')
def deck():
    return render_template('deck.html')

@static_bp.route('/api_docs')
def api_docs():
    return render_template('api_docs.html')

@static_bp.route('/monitor_docs')
def monitor_docs():
    return render_template('monitor_docs2.html')

@static_bp.route('/case_study')
def case_study():
    return render_template('case_study.html')

@static_bp.route('/kb_cite')
def kb_cite():
    return render_template('kb_cite.html')

@static_bp.route('/kb_summary')
def kb_summary():
    return render_template('kb_summary.html')

@static_bp.route('/api_use')
def api_use():
    return render_template('api_use.html')

@static_bp.route('/other')
def other():
    return render_template('miro.html')

