from flask import Flask, Blueprint
from md.backend import active_db

home_app = Blueprint('home', __name__)
home_app.active_mdb = active_db

import md.views.home.views
