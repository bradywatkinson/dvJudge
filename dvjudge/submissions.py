# all the imports
from contextlib import closing
from flask import Flask, request, session, g, redirect, url_for, \
     abort, render_template
import os
from core import query_db

from dvjudge import app

@app.route('/submissions')
def show_submissions():
    if 'logged_in' not in session or session['logged_in'] == False:
        abort(401)
    # Convert session user to a user ID
    cur = query_db('select id from users where username = ?', [session['user']], one=True)
    if cur is not None:
        user_id = cur[0]
    else:
        abort(401)

    # Get stuff from the database
    cur = query_db('''select s.id, user_id, challenge_id, timestamp, status, status_info, c.name, language '''
                   '''from submissions s join challenges c on s.challenge_id = c.id where user_id = ?''', [user_id])
    # Produce an array of hashes that looks something like:
    # [{id->'1', user_id->'5', problem_name->'2', timestamp->'<the time>', status->'Accepted', status_info->'Some Error', language->'C'}, {other hash}]  
    submissions = [dict(id=row[0],user_id=row[1],challenge_name=row[6],timestamp=row[3],status=row[4],status_info=row[5],language=row[7]) for row in cur]
    
    # Send it to submissions
    return render_template('submissions.html', submissions=submissions)

@app.route('/submissions/<id>')
def show_specific_submission(id):
    if 'logged_in' not in session or session['logged_in'] == False:
        abort(401)
    # look up DB for this partciular submission
    cur = query_db('''select s.id, user_id, challenge_id, timestamp, status, status_info, c.name '''
                   ''' from submissions s join challenges c on s.challenge_id = c.id where s.id = ?''', [id], one=True)
    _id = cur[0]

    # Convert user_id to username
    cur2 = query_db('select username from users where id = ?', [cur[1]], one=True)
    if cur is not None:
        user_id = cur2[0]
    else:
        abort(401)
 
    problem_name = cur[6]
    timestamp    = cur[3]
    status       = cur[4]
    status_info  = cur[5]

    # Send it to the page
    return render_template('submission.html', id=_id, user_id=user_id, problem_name=problem_name, timestamp=timestamp, status=status, status_info=status_info)
