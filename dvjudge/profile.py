from flask import render_template, session, request, abort, g
from dvjudge import app
from core import query_db, update_db
from comments import get_comments, post_comment
import hashlib

from werkzeug import secure_filename

from flask import Flask, request, session, g, redirect, url_for, \
     abort, render_template, flash
import os

# the allowable
ALLOWED_EXTENSIONS = set(['jpg', 'jpeg'])

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

    # check passwords are the same
    if pass1 != pass2:
        flash('Passwords do not match', 'error')
        return redirect(url_for('profile'))

    # check username does not already exist
    username_check = query_db('''select id from users where username = ? and id != ?''',[username, session['userid']], one=True)
    if username_check is not None:
        flash('Username is already taken','error')
        return redirect(url_for('profile'))

    # check email does not already exist
    email_check = query_db('''select id from users where email = ? and id != ?''',[email, session['userid']], one=True)
    if email_check is not None:
        flash('Email is already taken','error')
        return redirect(url_for('profile'))

    if pass1 != "" and pass2 != "":
        user_pass = query_db('''select salt from users where id = ?''',[session['userid']], one=True)
        hashed_password = hashlib.sha512(pass1 + user_pass[0]).hexdigest()
        update_db('''update users set username = ?, email = ?, password = ? where id = ?''', [username, email, hashed_password, session['userid']])

    else:
        update_db('''update users set username = ?, email = ? where id = ?''', [username, email, session['userid']])

    session['user'] = username
    return redirect(url_for('profile'))

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1] in ALLOWED_EXTENSIONS

@app.route('/updateprofilepic', methods=['POST'])
def updateprofilepic():
    file = request.files['file']
        
    
    # save the file
    if file and allowed_file(file.filename):
        filename = str(session['userid'])+"_profilepic.jpg"
        file.save(os.path.join(os.getcwd()+"/dvjudge/static", filename))
        session['profilepic']=True;

    session['image'] = session['image'] = '%s_profilepic.jpg' % session['userid']
    return redirect(url_for('profile'))
