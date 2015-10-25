from flask import render_template, session, request, abort
from dvjudge import app
from core import query_db, update_db

@app.route('/community/browse', methods=['GET'])
def community_browse():
    cur = query_db('select id, name from challenges where com_flag = 1')
    challenges = [dict(id=row[0],name=row[1]) for row in cur]
    # Retrieve category names
    cur = query_db('select name from categories');
    if cur:
        categories = [dict(name=row[0]) for row in cur]



    return render_template('browse.html', challenges=challenges, categories=categories, com_flag=1)

@app.route('/community/browse', methods=['POST'])
def community_browse_post():
    cur = query_db('select id, name from challenges where com_flag = 1')
    # Produce an array of hashes that looks something like:
    # [{id->'1', name->'some challenge name'}, {other hash}]  
    challenges = [dict(id=row[0],name=row[1]) for row in cur]
    # Retrieve category names
    cur = query_db('select name from categories');
    if cur:
        categories = [dict(name=row[0]) for row in cur]


    # User is searching
    if request.form.get('searchterm'):
        # Iterate over challenges, and only keep hashes (i.e. challenges) where the names match up
        name = request.form.get('searchterm')
        results = [challenge for challenge in challenges if name.lower() in challenge['name'].lower()]
        # Pass only those on
        com_flag = True
        return render_template('browse.html', challenges=results, searchterm=request.form.get('searchterm'), com_flag=com_flag)
    elif request.form.get('add') is not None:
        # Admin request to move challenges
        if session['user'] == "admin":
            for challenge in challenges:
                move_name = request.form.get(challenge['name'])
                if move_name:
                    move = "update challenges set com_flag=0 where name=?;"
                    update_db(move, [challenge['name']])
            cur = query_db('select id, name from challenges where com_flag = 1')
            challenges = [dict(id=row[0],name=row[1]) for row in cur]
    # Admin request to delete challenge
    elif request.form.get('delete_chal') is not None:
        if session['user'] == "admin":
            update_db('delete from challenges where name=?',[request.form.get('delete_chal')])
            cur = query_db('select id, name from challenges where com_flag = 1')
            # Produce an array of hashes that looks something like:
            # [{id->'1', name->'some challenge name'}, {other hash}]  
            challenges = [dict(id=row[0],name=row[1]) for row in cur]

    return render_template('browse.html', challenges=challenges, categories=categories, com_flag=1)


@app.route('/community/browse/<challenge_name>', methods=['GET'])
def community_browse_specific_challenge(challenge_name): 
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
    challenge_info = {'challenge_id': challenge_id, 'name': name, 'description': description, 'sample_tests': sample_tests, 'input_desc': input_desc, 'output_desc': output_desc}
    
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

    return render_template('challenge.html', challenge_info=challenge_info, output=info, code = code )
