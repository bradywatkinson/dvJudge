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
    if request.form["submit"] == 'signin':
        
        #retrieve username and password
        username = request.form['username']
        password = request.form['password']
        user_pass = query_db('select username, password, salt from users where username = ? or email = ?',[username,username], one=True)
        if user_pass is not None:
            print user_pass
            hashed_password = hashlib.sha512(password + user_pass[2]).hexdigest()
            if username == user_pass[0] and hashed_password == user_pass[1]:
                session['logged_in'] = True
                session['user'] = username
                flash('You were logged in')
            else:
                error += "Username and password do not match"
        else:
            error += "Username and password do not match"

    if request.form["submit"] == 'signup':
        #check if duplicate username
        username = request.form['username']
        value = query_db('select * from users where username = ?',[username], one=True)
        if value is not None:
            error += "Username is already taken\n"
        #check if emails match up
        email = request.form['email']
        #confirmemail = request.form['confirmemail']
        #if not email or email != request.form['confirmemail']:
         #   error += "Emails do not match\n"
        #check if passwords match up
        password = request.form['password']
        if len(password) < 6:
            error += "Passwords need to be 6 characters or longer"
        if not password or password != request.form['confirmpassword']:
            error += "Passwords do not match\n"
        #if form entry was not succesful return errors
        #if error != "":
            #return render_template('signup.html', error=error, username=username, email=email, confirmemail=confirmemail)
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
        flash(error)
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
        return render_template('userprofile.html', username=session['user'])
    else:
        flash('You need to login before you can access this page')
        return redirect(url_for('show_mainpage'))