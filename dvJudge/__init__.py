from flask import Flask

# create our little application :)
app = Flask(__name__)
#app.config.from_object(__name__)
#Load server settings from config file
app.config.from_pyfile('settings.cfg', silent=True)

import dvjudge.core
import dvjudge.browse
import dvjudge.submit
import dvjudge.upload
import dvjudge.userauth
