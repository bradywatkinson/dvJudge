from flask import render_template
from dvjudge import app


#this page handles the error codes

@app.errorhandler(500)
def error_500():
	return render_template("show_mainpage.html")

@app.errorhandler(400)
def error_400():
	return render_template("show_mainpage.html")

@app.errorhandler(404)
def error_404():
	return render_template("show_mainpage.html")

