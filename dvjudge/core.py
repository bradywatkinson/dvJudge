# all the imports
from contextlib import closing
from flask import Flask, request, session, g, redirect, url_for, \
     abort, render_template, flash
import os

from dvjudge import app

@app.route('/')
def show_mainpage():
    session['page'] = "show_mainpage"
    return render_template('show_mainpage.html')

def make_dicts(cursor, row):
    return dict((cur.description[idx][0], value)
                for idx, value in enumerate(row))

def query_db(query, args=(), one=False):
    cur = g.db.execute(query, args)
    rv = cur.fetchall()
    cur.close()
    return (rv[0] if rv else None) if one else rv

#update database
def update_db(query, args=()):
	
	g.db.execute(query, args)
	g.db.commit()

if __name__ == '__main__':
    app.run()
