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
        name        = cur[1]
        description = cur[2]
        sample_tests= cur[5]
        input_desc  = cur[6]
        output_desc = cur[7]
    else:
        abort(404)

    challenge_info = {'challenge_id': challenge_id, 'name': name, 'description': description, 'sample_tests': sample_tests, 
                'input_desc': input_desc, 'output_desc': output_desc, 'languages':supported_languages}

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
    question_comments = get_comments(challenge_id)
      
    return render_template('challenge.html', challenge_info=challenge_info, output=info, code=code, playlists=playlists, language=language, comments=question_comments, data=json.dumps(data))


