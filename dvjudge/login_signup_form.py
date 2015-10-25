from flask import render_template, session, request, flash, url_for, redirect, abort, g
from dvjudge import app
from core import query_db
import hashlib
import subprocess
import os
import uuid

@app.route('/login_signup_form', methods=['POST'])
def login_signup_form():
    error = ""
    # print request.form['page']
    if request.form["submit"] == 'signin':
        
        #retrieve username and password
        username = request.form['username']
        password = request.form['password']
        user_pass = query_db('select id, username, password, salt, image from users where username = ? or email = ?',[username,username], one=True)
        if user_pass is not None:
            #print user_pass
            hashed_password = hashlib.sha512(password + user_pass[3]).hexdigest()
            if username == user_pass[1] and hashed_password == user_pass[2]:
                session['userid'] = user_pass[0]
                session['logged_in'] = True
                session['user'] = username
                session['image'] = user_pass[4]
                flash('You were logged in','alert')
            else:
                error += "Username and password do not match"
        else:
            error += "Username and password do not match"

    #print request.form["submit"]
    if request.form["submit"] == 'signup':
        #check if duplicate username
        username = request.form['username']
        value = query_db('select * from users where username = ?',[username], one=True)
        if value is not None:
            error += "Username is already taken\n"
        email = request.form['email']
        password = request.form['password']
        if len(password) < 6:
            error += "Passwords need to be 6 characters or longer"
        if not password or password != request.form['confirmpassword']:
            error += "Passwords do not match\n"
        else:
            #hash password and salt
            salt = uuid.uuid4().hex
            hashed_password = hashlib.sha512(password + salt).hexdigest()
            #submit info to the database
            g.db.execute("insert into users (username, email, password, salt) values (?, ?, ?, ?)", [username, email, hashed_password, salt])
            g.db.commit()

            flash('You successfully created an account','alert')
            session['logged_in'] = True
            
            session['user'] = username
            session['userid'] = query_db('''select last_insert_rowid()''')[0][0];
            session['image'] = "default_profile.jpg"
            
            flash('You were logged in','alert')
    if error != "":
        flash(error,'error')
        # session['error'] = error
    if request.form['page'] == "browse_specific_challenge":
        return redirect(url_for('browse_specific_challenge', challenge_name=request.form['challenge_name']))
    if request.form['page'] == "forums_browse":
        return redirect(url_for('forums_browse', forum_problem=request.form['forum_problem']))
    # if "forum_question" in request.form:
    if request.form['page'] == "forums_question":
        return redirect(url_for('forums_question', forum_problem=request.form['forum_problem'], forum_question=request.form['forum_question']))
    return redirect(url_for(request.form['page']))

@app.route('/logout')
def logout():
    session.pop('logged_in', None)
    session.pop('user', None)
    session.pop('userid', None)
    session.pop('image', None)
    flash('You were logged out','alert')
    return redirect(url_for('show_mainpage'))
