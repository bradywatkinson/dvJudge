from flask import Flask, request, session, g, redirect, url_for, \
     abort, render_template, flash
from dvjudge import app
import hashlib
import uuid

@app.route('/login', methods=['GET', 'POST'])
def login():
    error = ""
    if request.method == 'POST':
        #retrieve username and password
        username = request.form['username']
        password = request.form['password']
        cur = g.db.execute("select username, password, salt from users where username='%s' " % username)
        user_pass = cur.fetchone()
        if user_pass:
            hashed_password = hashlib.sha512(password + user_pass[2]).hexdigest()
            if username == user_pass[0] and hashed_password == user_pass[1]:
                session['logged_in'] = True
                session['user'] = username
                flash('You were logged in')
                return redirect(url_for('show_mainpage'))
            else:
                error += "Username and password do not match"
        else:
            error += "Username and password do not match"

    return render_template('login.html', error=error)
    
@app.route('/signup', methods=['GET', 'POST'])
def signup():
    error = ""
    if request.method == 'POST':
        #check if duplicate username
        username = request.form['username']
        cursor = g.db.cursor()
        cursor.execute("select * from users where username='%s'" % (username))
        value = cursor.fetchone()
        if value != None:
            error += "Username is already taken\n"
        #check if emails match up
        email = request.form['email']
        confirmemail = request.form['confirmemail']
        if not email or email != request.form['confirmemail']:
            error += "Emails do not match\n"
        #check if passwords match up
        password = request.form['password']
        if len(password) < 6:
            error += "Passwords need to be 6 characters or longer"
        if not password or password != request.form['confirmpassword']:
            error += "Passwords do not match\n"
        #if form entry was not succesful return errors
        if error != "":
            return render_template('signup.html', error=error, username=username, email=email, confirmemail=confirmemail)
        else:
            #hash password and salt
            salt = uuid.uuid4().hex
            hashed_password = hashlib.sha512(password + salt).hexdigest()
            #submit info to the database
            g.db.execute("insert into users (username, email, password, salt) values ('%s', '%s', '%s', '%s')" % (username, email, hashed_password, salt))
            g.db.commit()
            flash('You successfully created an account')
            session['logged_in'] = True
            session['user'] = username
            flash('You were logged in')
            return redirect(url_for('show_mainpage'))
    return render_template('signup.html', error=error)


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
