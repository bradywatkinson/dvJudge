# all the imports
from contextlib import closing
import sqlite3
from flask import Flask, request, session, g, redirect, url_for, \
     abort, render_template, flash
import os

# configuration
DATABASE = '/tmp/dvjudge.db'
DEBUG = True
SECRET_KEY = 'development key'
USERNAME = 'admin'
PASSWORD = 'default'

# create our little application :)
app = Flask(__name__)
app.config.from_object(__name__)

app.config.from_envvar('DVJUDGE_SETTINGS', silent=True)

def connect_db():
    return sqlite3.connect(app.config['DATABASE'])


def init_db():
    with closing(connect_db()) as db:
        with app.open_resource('schema.sql', mode='r') as f:
            db.cursor().executescript(f.read())
        db.commit() 

@app.before_request
def before_request():
    g.db = connect_db()

@app.teardown_request
def teardown_request(exception):
    db = getattr(g, 'db', None)
    if db is not None:
        db.close()

@app.route('/')
def show_entries():
    cur = g.db.execute('select title, text from entries order by id desc')
    entries = [dict(title=row[0], text=row[1]) for row in cur.fetchall()]
    return render_template('show_entries.html', entries=entries)

@app.route('/add', methods=['POST'])
def add_entry():
    if not session.get('logged_in'):
        abort(401)
    g.db.execute('insert into entries (title, text) values (?, ?)',
                 [request.form['title'], request.form['text']])
    g.db.commit()
    flash('New entry was successfully posted')
    return redirect(url_for('show_entries'))

@app.route('/upload_code', methods=['POST'])
def upload_code():
    if not session.get('logged_in'):
        abort(401)
    # Grab the source code from the form and put it in a file
    f = open('code.c', 'w')
    f.write (request.form['text'])
    f.close()

    # Compile it 
    result = os.system('gcc code.c &> output')
    os.system('rm code.c') # clean up

    # GCC had a compile error... send it back to the user
    if result != 0:
        f = open('output', 'r')
        result = f.read()
        f.close()
        
        # Clean up
        os.system('rm output')
        
        # Render upload_code, pass the code back as well.
        return render_template('upload_code.html', result="COMPILE ERROR:\n" + result, code=request.form['text'])
    else:
        # Run the program and capture it's output
        os.system('./a.out > output')

        # Clean up
        os.system('rm a.out')

        # Lets test it against '1 2 3 4 5'
        result = os.system('diff -b output problems/1/solution &> /dev/null')
       
        # Clean up 
        os.system('rm output')

        # If result is 0, great, solved 
        if result == 0:
            return render_template('upload_code.html', result="SOLVED!", code=request.form['text'])
        else:
            return render_template('upload_code.html', result="WRONG ANSWER!", code=request.form['text'])

@app.route('/login', methods=['GET', 'POST'])
def login():
    error = None
    if request.method == 'POST':
        if request.form['username'] != app.config['USERNAME']:
            error = 'Invalid username'
        elif request.form['password'] != app.config['PASSWORD']:
            error = 'Invalid password'
        else:
            session['logged_in'] = True
            flash('You were logged in')
            return redirect(url_for('show_entries'))
    return render_template('login.html', error=error)

@app.route('/logout')
def logout():
    session.pop('logged_in', None)
    flash('You were logged out')
    return redirect(url_for('show_entries'))

@app.route('/upload')
def upload():
    error = None
    if not session.get('logged_in'):
        abort(401)
    return render_template('upload_code.html', error=error) 

if __name__ == '__main__':
    app.run()
