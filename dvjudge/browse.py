from flask import render_template, session, request, abort, g
from dvjudge import app
from core import query_db


@app.route('/playlist', methods=['GET'])
def show_playlist():
    cur = query_db('select id, name from challenges')
    challenges = [dict(id=row[0],name=row[1]) for row in cur]
    return render_template('playlist.html', challenges=challenges)


@app.route('/browse', methods=['GET'])
def browse():
    cur = query_db('select id, name from challenges')
    challenges = [dict(id=row[0],name=row[1]) for row in cur]
    return render_template('browse.html', challenges=challenges)

@app.route('/browse', methods=['POST'])
def browse_search():
    name = request.form.get('searchterm')
    cur = query_db('select id, name from challenges')
    # Produce an array of hashes that looks something like:
    # [{id->'1', name->'some problem name'}, {other hash}]  
    challenges = [dict(id=row[0],name=row[1]) for row in cur]
    # Iterate over challenges, and only keep hashes (i.e. problems) where the names match up
    results = [challenge for challenge in challenges if name.lower() in challenge["name"].lower()]
    # Pass only those on
    return render_template('browse.html', challenges=results, searchterm=request.form.get('searchterm'))

@app.route('/browse/<problem_name>', methods=['GET'])
def browse_specific_problem(problem_name): 
    cur = query_db('select * from challenges where name = ?', [problem_name], one=True)
    if cur is not None:
        problem_id  = cur[0]
        name        = cur[1]
        description = cur[2]
        sample_tests= cur[5]
        input_desc  = cur[6]
        output_desc = cur[7]
    else:
        abort(404)
    problem_info = {'problem_id': problem_id, 'name': name, 'description': description, 'sample_tests': sample_tests, 'input_desc': input_desc, 'output_desc': output_desc}
    
    #Check if it's a redirect from submission and the program 
    #has produced output
    #Stored in session cookie
    if 'output' in session:
        info = session['output']
        session.pop('output', None)
    else:
        info = None
    #check for submitted code from user
    if 'code' in session:
        code = session['code']
        session.pop('code', None)
    else:
        code = None

    # Prepare playlist information for the dropdown if user logged in
    playlists = {} 
    if 'user' in session:
       username = session['user']
       # Convert user session to user ID
       cur = query_db('select id from users where username = ?', [username], one=True)
       if cur is not None:
           # Retrieve the playlists available to this user
           cur = query_db('select * from playlists where owner_id = ?', [cur[0]])
            
           # Build a dictionary to pass to the page later
           playlists = [dict(id=row[0],name=row[1]) for row in cur]
       else:
           abort(401)
        
    return render_template('problem.html', problem_info=problem_info, output=info, code=code, playlists=playlists)

@app.route('/playlists')
def show_playlists():
    if 'user' in session:
       username = session['user']
       # Convert user session to user ID
       cur = query_db('select id from users where username = ?', [username], one=True)
       if cur is not None:
           # Retrieve the playlists available to this user
           cur = query_db('select * from playlists where owner_id = ?', [cur[0]])
            
           # Build a dictionary to pass to the page later
           # Dictionary contains playlist name, id, and which challenges belong to it
           playlists = [dict(id=row[0],name=row[1],challenges=row[2]) for row in cur]

           # Passing playlists.html all the playilst info in a hash
           return render_template('playlists.html', playlists=playlists)
       else:
           abort(401)
    else:
        abort(401)

@app.route('/new_playlist', methods=['POST'])
def create_playlist():
    if request.form['playlist_name'] is None:
        abort(400)
    else:
        playlist_name = request.form['playlist_name']

    if 'user' in session:
        username = session['user']
        cur = query_db('select id from users where username = ?', [username], one=True)
        if cur is not None:
            user_id = cur[0]
            g.db.execute('insert into playlists (name, owner_id, challenges) values (?, ?, "")', [playlist_name, user_id])
            g.db.commit()
            # Render template something something?
            return "New playlist created with name " + playlist_name
        else:
            abort(401)
    else:
        abort(401)

        
