from flask import render_template, request, session, abort, g, flash
from dvjudge import app
from core import query_db

@app.route('/community', methods=['GET', 'POST'])
def community():
	return render_template('community.html') 