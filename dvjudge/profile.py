from flask import render_template, session, request, abort, g
from dvjudge import app
from core import query_db, update_db
from comments import get_comments, post_comment

from flask import Flask, request, session, g, redirect, url_for, \
     abort, render_template, flash
import os

@app.route('/profile', methods=['GET'])
def profile():
    cur = query_db('select * from users where id = ?', [session['userid']], one=True)
    if cur is not None:
        user_id     = cur[0]
        username    = cur[1]
        email       = cur[2]
    return render_template('profile.html',userid=user_id,username=username,email=email)

@app.route('/updateprofile', methods=['POST'])
def updateprofile():
    email    = request.form['email']
    username = request.form['username']
    pass1    = request.form['pass1']
    pass2    = request.form['pass2']
    if pass1 != pass2:
        flash('Passwords do not match')
        return redirect(url_for('profile'))
    update_db('''update users set username = ?, email = ?, password = ? where id = ?''', [username, email, pass1, session['userid']])
    #g.db.execute('''update users set username, email, password where id = ?''', [session['userid']])
    #g.db.commit()
    return redirect(url_for('profile'))
