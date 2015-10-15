from flask import render_template, session, request, abort, g
from dvjudge import app
from core import query_db, update_db
from comments import get_comments, post_comment
import re
import json

@app.route('/browse/<challenge_name>', methods=['GET', 'POST'])
def browse_specific_challenge(challenge_name): 
    supported_languages = {'C', 'Python', 'Java', 'C++'}
    data = {'C':"// enter code here", 'Python':"# enter code here", 'Java':"// enter code here", 'C++':"// enter code here"}

    cur = query_db('select * from challenges where name = ?', [challenge_name], one=True)
    if cur is not None:
        challenge_id  = cur[0]
        name          = cur[1]
        description   = cur[2]
        sample_tests  = cur[5]
        input_desc    = cur[6]
        output_desc   = cur[7]
        com_flag      = cur[8]
    else:
        abort(404)

    challenge_info = {'challenge_id': challenge_id, 'name': name, 'description': description, 'sample_tests': sample_tests, 
                'input_desc': input_desc, 'output_desc': output_desc, 'languages':supported_languages, 'com_flag':com_flag}

    #check for posted comment
    if request.method == 'POST':
        comment = request.form['comment']
        if comment:
            post_comment(session['user'], challenge_id, comment)
  
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

    # Variables for playlist add
    exists = False
    playlist_name = request.args.get('playlist_name')

    # Prepare playlist information for the dropdown if user logged in
    playlists = {} 
    if 'user' in session:
        username = session['user']
        # Convert user session to user ID
        cur = query_db('select id from users where username = ?', [username], one=True)
        if cur is not None:
            user_id = cur[0]
            # Retrieve the playlists available to this user
            cur = query_db('select * from playlists where owner_id = ?', [cur[0]])
            
            # Build a dictionary to pass to the page later
            playlists = [dict(id=row[0],name=row[1]) for row in cur]

            # Selected to add to playlist
            if playlist_name:
                add_list = query_db('select * from playlists where owner_id = ? and name = ?',
                    [user_id, playlist_name], one=True)
                # Check if playlist name exists
                if add_list is not None:
                    challenge_ids = add_list[3]
                    # Check that challenge IDs is not an empty string
                    if challenge_ids:
                        id_list = [int(s) for s in challenge_ids.split('|')]
                        if challenge_id not in id_list:
                            challenge_ids += "|" + str(challenge_id)
                        # if challenge id is in list, set the exists flag for the alert
                        else:
                            exists = True

                    # Add id to playlist
                    else:
                        challenge_ids = str(challenge_id)
                    add_str = "update playlists set challenges=? where name=? and owner_id=?;"
                    update_db(add_str, [challenge_ids,playlist_name,user_id])
                # Playlist name not found
                else:
                    playlist_name = ""
        else:
           abort(401)
  
    #insert the comments section
    question_comments = get_comments(challenge_id)
      
    return render_template('challenge.html', challenge_info=challenge_info, output=info, code=code, playlists=playlists,
        language=language, comments=question_comments, data=json.dumps(data), playlist_name=playlist_name, exists=exists)


