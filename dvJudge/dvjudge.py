# all the imports
from contextlib import closing
import sqlite3
from flask import Flask, request, session, g, redirect, url_for, \
     abort, render_template, flash
import os

# create our little application :)
app = Flask(__name__)
#app.config.from_object(__name__)
#Load server settings from config file
app.config.from_pyfile('settings.cfg', silent=True)

####### Database functions ##########
def connect_db():
    return sqlite3.connect(app.config['DATABASE'])

def init_db():
    with closing(connect_db()) as db:
        with app.open_resource('schema.sql', mode='r') as f:
            db.cursor().executescript(f.read())
        db.commit()

def populate_db():
    with closing(connect_db()) as db:
        with app.open_resource('db_populate.sql', mode='r') as f:
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
#############################################

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

@app.route('/login', methods=['GET', 'POST'])
def login():
    error = ""
    if request.method == 'POST':
        #retrieve username and password
        username = request.form['username']
        password = request.form['password']
        cur = g.db.execute("select username, password from users where username='%s' " % username)
        user_pass = cur.fetchone()
        if user_pass:
            if username == user_pass[0] and password == user_pass[1]:
                session['logged_in'] = True
                session['user'] = username
                flash('You were logged in')
                return redirect(url_for('show_entries'))
            else:
                error += "Username and password don't match"
        else:
            error += "Username and password don't match"

    return render_template('login.html', error=error)


@app.route('/signup', methods=['GET', 'POST'])
def signup():
    error = ""
    if request.method == 'POST':
        #check if duplicate username
        username = request.form['username']
        cursor = g.db.cursor()
        cursor.execute("select exists(select 1 from users where username='%s') " % (username)) #ensure it is not open to sql injection
        if not cursor.fetchone():
            error += "Username is already taken\n"
            for search_result in username_search:
                error += search_result + "\n"
        #check if emails match up
        email = request.form['email']
        confirmemail = request.form['confirmemail']
        if not email or email != request.form['confirmemail']:
            error += "Emails don't match\n"
        #check if passwords match up
        password = request.form['password']
        if len(password) < MIN_PASSWORD_LENGTH:
            error += "Passwords need to be 6 characters or longer"
        if not password or password != request.form['confirmpassword']:
            error += "Passwords don't match\n"
        #if form entry was not succesful return errors
        if error != "":
            print "error message is " + error
            return render_template('signup.html', error=error, username=username, email=email, confirmemail=confirmemail)
        else:
            #submit info to the database
            return_value = g.db.execute("insert into users (username, email, password) values ('%s', '%s', '%s')" % (username, email, password))
            flash('You successfully created an account')
            session['logged_in'] = True
            session['user'] = username      
            return redirect(url_for('show_entries'))
    return render_template('signup.html', error=error)

@app.route('/logout')
def logout():
    session.pop('logged_in', None)
    session.pop('user', None)
    flash('You were logged out')
    return redirect(url_for('show_entries'))

@app.route('/myprofile')
def myprofile():
    if session['user']:
        return render_template('userprofile.html', username=session['user'])
    else:
        flash('You need to login before you can access this page')
        return redirect(url_for('show_entries'))


def make_dicts(cursor, row):
    return dict((cur.description[idx][0], value)
                for idx, value in enumerate(row))

def query_db(query, args=(), one=False):
    cur = g.db.execute(query, args)
    rv = cur.fetchall()
    cur.close()
    return (rv[0] if rv else None) if one else rv

# For Uploading problems
@app.route('/upload', methods=['GET', 'POST'])
def upload():
    if not session['logged_in']:
        abort(401)
    
    # Someone is trying to submit a new problem
    if request.method == 'POST':
        name = request.form.get('name')
        description = request.form.get('description')
        # TODO: Validate?
        add_problem (name, description) 
        flash ("Problem added successfully")

    return render_template('upload_problem.html') 

def add_problem(name, description):
    g.db.execute ("""insert into challenges (name,description,input,output,sample_input,sample_output)
                    values (?, ?, 'test', 'test', null, null)""", [name, description])
    g.db.commit()

@app.route('/browse', methods=['GET'])
def browse():
    cur = query_db('select id, name from challenges')
    challenges = [dict(id=row[0],name=row[1]) for row in cur]
    return render_template('browse.html', challenges=challenges)

@app.route('/browse/<problem_id>', methods=['GET'])
def browse_specific_problem(problem_id):
    cur = query_db('select id, description, name from challenges where id = ?', [problem_id], one=True)
    if cur is not None:
        name = cur[2]
        description = cur[1]
    else:
        abort(404)
    problem_info = {'problem_id': problem_id, 'name': name, 'description': description}
    return render_template('problem.html', problem_info=problem_info)

@app.route('/submit', methods=['POST'])
def submit_specific_problem():
    flash ("Successfully submitted for problem " + request.args.get('problem_id'))
    # TODO: No validation
    return browse() 

if __name__ == '__main__':
    app.run()
