from flask import render_template, session, request, abort, redirect, url_for
from dvjudge import app
from core import query_db, update_db
from browse import do_browse, do_browse_post

@app.route('/community/browse', methods=['GET'])
def community_browse():

    vals = do_browse(com=True)
    return render_template('browse.html', challenges=vals[0], categories=vals[1], com_flag=True)

@app.route('/community/browse', methods=['POST'])
def community_browse_post():
    
    cur = query_db('select id, name, submitter_id from challenges where com_flag = 1')
    # Produce an array of hashes that looks something like:
    # [{id->'1', name->'some challenge name'}, {other hash}]  
    challenges = [dict(id=row[0],name=row[1],submitter_id=row[2]) for row in cur]
    # Retrieve category names
    cur = query_db('select name from categories');
    if cur:
        categories = [dict(name=row[0]) for row in cur]

    if request.form.get('add') is not None:
        # Admin request to move challenges
        if session['user'] == "admin":
            for challenge in challenges:
                move_name = request.form.get(challenge['name'])
                if move_name:
                    move = "update challenges set com_flag=0 where name=?;"
                    update_db(move, [challenge['name']])
            cur = query_db('select id, name, submitter_id from challenges where com_flag = 1')
            challenges = [dict(id=row[0],name=row[1],submitter_id=row[2]) for row in cur]
    # Admin request to delete challenge
    elif request.form.get('delete_chal') is not None:
        if session['user'] == "admin":
            update_db('delete from challenges where name=?',[request.form.get('delete_chal')])
            cur = query_db('select id, name, submitter_id from challenges where com_flag = 1')
            # Produce an array of hashes that looks something like:
            # [{id->'1', name->'some challenge name'}, {other hash}]  
            challenges = [dict(id=row[0],name=row[1],submitter_id=row[2]) for row in cur]

    # Convert user_ids to usernames
    for challenge in challenges:
        lookup = query_db("select username from users where id = ?", [challenge['submitter_id']], one=True)
        if lookup is not None:
            challenge['submitter_id'] = lookup[0]
        else:
            challenge['submitter_id'] = "DvJudge"

    vals = do_browse_post(com=True)
    return render_template('browse.html', challenges=vals[0], searchterm=vals[1], categories=vals[2], no_completed=vals[3], com_flag=True)

@app.route('/community/browse/<challenge_name>', methods=['GET'])
def community_browse_specific_challenge(challenge_name):

    return redirect(url_for('browse_specific_challenge', challenge_name=challenge_name))
