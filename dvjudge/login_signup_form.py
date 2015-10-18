from flask import render_template, session, request, flash, url_for, redirect, abort, g
from dvjudge import app
from core import query_db
import hashlib
import subprocess
import os.path
import uuid

@app.route('/login_signup_form', methods=['POST'])
def login_signup_form():
    error = ""
    # print request.form['page']
    if request.form["submit"] == 'signin':
        
        #retrieve username and password
        username = request.form['username']
        password = request.form['password']
        user_pass = query_db('select username, password, salt from users where username = ? or email = ?',[username,username], one=True)
        if user_pass is not None:
            hashed_password = hashlib.sha512(password + user_pass[2]).hexdigest()
            if username == user_pass[0] and hashed_password == user_pass[1]:
                session['logged_in'] = True
                session['user'] = username
                flash('You were logged in')
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

            flash('You successfully created an account')
            session['logged_in'] = True
            
            session['user'] = username
            
            flash('You were logged in')
    if error != "":
        # flash(error)
        session['error'] = error
    if request.form['page'] == "browse_specific_challenge":
        return redirect(url_for('browse_specific_challenge', challenge_name=request.form['challenge_name']))
    if request.form['page'] == "forums_browse":
        return redirect(url_for('forums_browse', forum_problem=request.form['forum_problem']))
    return redirect(url_for(request.form['page']))


@app.route('/logout')
def logout():
    session.pop('logged_in', None)
    session.pop('user', None)
    flash('You were logged out')
    return redirect(url_for('show_mainpage'))

@app.route('/myprofile')
def myprofile():
    if 'user' in session:
        # Lookup data they need for the profile page
        data = {}
        challenge_string = ""
        cur = query_db('select solved_challenges from users where username = ?', [session['user']], one=True)
        if cur is not None and cur[0] is not None:
            solved_challenges = cur[0]
            # split solved_challenges on '|' character
            for word in solved_challenges.split('|'):
                challenge_string = challenge_string + " " + word

        data["solved_challenges"] = challenge_string
        return render_template('userprofile.html', username=session['user'], data=data)
    else:
        flash('You need to login before you can access this page')
        return redirect(url_for('show_mainpage'))
