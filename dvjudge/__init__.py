from flask import Flask, g
from contextlib import closing
import sqlite3

# create our little application :)
app = Flask(__name__)
#app.config.from_object(__name__)
#Load server settings from config file
app.config.from_pyfile('settings.cfg', silent=True)

####### Database functions ##########
def connect_db():
    return sqlite3.connect(app.config['DATABASE'])

def init_db():
    with closing(connect_db()) as db:
        with app.open_resource('schema.sql', mode='r') as f:
            db.cursor().executescript(f.read())
        db.commit()

def populate_db():
    with closing(connect_db()) as db:
        with app.open_resource('db_populate.sql', mode='r') as f:
           db.cursor().executescript(f.read())
        db.commit()
@app.before_request
def before_request():
    g.db = connect_db()

@app.teardown_request
def teardown_request(exception):
    db = getattr(g, 'db', None)
    if db is not None:
        db.close()
#############################################

import dvjudge.core
import dvjudge.browse
import dvjudge.submit
import dvjudge.upload
import dvjudge.community
import dvjudge.community_browse
import dvjudge.login_signup_form
import dvjudge.submissions
import dvjudge.profile
import dvjudge.challenge
import dvjudge.forums
import dvjudge.comments
import dvjudge.playlists