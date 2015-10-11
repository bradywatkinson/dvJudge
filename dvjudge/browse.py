from flask import render_template, session, request, abort, g
from dvjudge import app
from core import query_db, update_db
from comments import get_comments, post_comment
import re

@app.route('/browse', methods=['GET'])
def browse():
    cur = query_db('select id, name from challenges where com_flag = 0')
    challenges = [dict(id=row[0],name=row[1]) for row in cur]
    return render_template('browse.html', challenges=challenges)

@app.route('/browse', methods=['POST'])
def browse_search():
    name = request.form.get('searchterm')
    cur = query_db('select id, name from challenges where com_flag = 0')
    # Produce an array of hashes that looks something like:
    # [{id->'1', name->'some problem name'}, {other hash}]  
    challenges = [dict(id=row[0],name=row[1]) for row in cur]
    # Iterate over challenges, and only keep hashes (i.e. problems) where the names match up
    results = [challenge for challenge in challenges if name.lower() in challenge["name"].lower()]
    # Pass only those on
    return render_template('browse.html', challenges=results, searchterm=request.form.get('searchterm'))

@app.route('/browse/<problem_name>', methods=['GET', 'POST'])
def browse_specific_problem(problem_name): 
    supported_languages = ['C', 'Python', 'Java', 'C++']

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

    problem_info = {'problem_id': problem_id, 'name': name, 'description': description, 'sample_tests': sample_tests, 
                'input_desc': input_desc, 'output_desc': output_desc, 'languages':supported_languages}

    #check for posted comment
    if request.method == 'POST':
        comment = request.form['comment']
        if comment:
            post_comment(session['user'], problem_id, comment)
  
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

    if 'language' in session:
        language = session['language']
        session.pop('language', None)
    else:
        language = 'C'
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
  
    #insert the comments section
    question_comments = get_comments(problem_id)
      
    return render_template('problem.html', problem_info=problem_info, output=info, code=code, playlists=playlists, in_use = language, comments=question_comments)

@app.route('/test', methods=['POST'])
def test():
    name = request.form.get('del')

    return "Hello" + name



@app.route('/playlists', methods=['GET', 'POST'])
def show_playlists():
    if 'user' in session:
        username = session['user']
        # Convert user session to user ID
        cur = query_db('select id from users where username = ?', [username], one=True)
        if cur is not None:
            owner_id = str(cur[0])
            # Check if selected 'Delete Playlist'
            del_name = request.form.get('delete_list')
            if del_name:
                update_db('delete from playlists where owner_id=? and name=?',[owner_id, del_name])

            # Retrieve the playlists available to this user
            cur = query_db('select * from playlists where owner_id = ?', [cur[0]])
                
            # Build a dictionary to pass to the page later
            # Dictionary contains playlist name, id, and which challenges belong to it
            playlists = [dict(id=row[0],name=row[1],challenges=row[3]) for row in cur]
            if playlists:
                selected_name = request.form.get('selected_name')
                selection = playlists[0]
                if selected_name is not None:
                    for play in playlists:
                        if play['name'] == selected_name:
                            selection = play


                cur = query_db('select id, name from challenges')
                # Produce an array of hashes that looks something like:
                # [{id->'1', name->'some problem name'}, {other hash}]  
                challenges = [dict(id=row[0],name=row[1]) for row in cur]
                challenge_list = []
                # Determine whether Submit Changes was pressed
                to_reorder = request.form.get('reorder')
                if to_reorder:
                    reorder_entry = {}
                    # Match each challenge to their new order
                    for challenge in challenges:
                        if request.form.get(challenge['name']):
                            chal_order = int(request.form.get(challenge['name']))
                            chal_id = int(challenge['id'])
                            reorder_entry[chal_order] = chal_id

                    # Generate an order string to insert into the database
                    new_order = ""
                    for key in reorder_entry:
                        if not new_order:
                            new_order = str(reorder_entry[key])
                        else:
                            new_order += "|" + str(reorder_entry[key])

                    reorder_str = "update playlists set challenges=? where name=? and owner_id=?;"
                    update_db(reorder_str, [new_order,selection['name'],owner_id])
                    challenge_ids = new_order
                else:
                    challenge_ids = selection['challenges']

                if challenge_ids:
                    # Obtain a list of in order challenge ids for a playlist
                    id_list = [int(s) for s in challenge_ids.split('|')]

                    for id in id_list:
                        challenge_list.append(challenges[id-1])
            else:
                playlists = None
                selection = None
                challenge_list = None

            # Passing playlists.html all the playilst info in a hash
            return render_template('playlists.html', playlists=playlists,
                        selection=selection, challenge_list=challenge_list)
        else:
            abort(401)
    else:
        abort(401)

@app.route('/new_playlist', methods=['GET'])
def show_playlist_form():
    if 'user' in session:
        cur = query_db('select id, name from challenges')
        challenges = [dict(id=row[0],name=row[1]) for row in cur]
        return render_template('new_playlist.html', challenges=challenges)
    else:
        abort(401)

@app.route('/new_playlist', methods=['POST'])
def create_new_playlist():
    if 'user' in session:
        username = session['user']
        cur = query_db('select id from users where username = ?', [username], one=True)
        if cur is not None:
            user_id = cur[0]
            # Set fields to check to false and grab playlist name
            no_name = False
            conflict_name = False
            new_name = None
            playlist_name = request.form.get('playlist_name')
            temp = re.sub('[\s+]', '', playlist_name)

            cur = query_db('select id, name from challenges')
            challenges = [dict(id=row[0],name=row[1]) for row in cur]

            # If invalid playlist name, flash an alert
            if not request.form.get('playlist_name') or temp == "":
                no_name = True
            # Insert new playlist into database
            else:
                new_name = playlist_name
                cur2 = query_db('select * from playlists where owner_id = ? and name = ?',
                    [user_id, playlist_name], one=True)
                if cur2 is None:
                    challenge_ids = ""
                    for challenge in challenges:
                        id = request.form.get(challenge['name'])
                        if id:
                            if not challenge_ids:
                                challenge_ids = str(id)
                            else:
                                challenge_ids += "|" + str(id)
                    g.db.execute('insert into playlists (name, owner_id, challenges) values (?, ?, ?)',
                        [playlist_name, user_id, challenge_ids])
                    g.db.commit()  
                else:
                    conflict_name = True  

            return render_template('new_playlist.html', challenges=challenges,
                                no_name=no_name, new_name = new_name, conflict_name=conflict_name)
        else:
            abort(401)
    else:
        abort(401)
