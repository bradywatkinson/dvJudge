from flask import render_template, session, request, abort, g
from dvjudge import app
from core import query_db, update_db
from comments import get_comments, post_comment

@app.route('/browse', methods=['GET'])
def browse():
    # com_flag of 2 signfies admin chosen challenges that can be attempted by anyone
    cur = query_db('select id, name from challenges where com_flag = 0 or com_flag = 2')
    challenges = [dict(id=row[0],name=row[1]) for row in cur]

    # Retrieve category names
    cur = query_db('select name from categories');
    if cur:
        categories = [dict(name=row[0]) for row in cur]

    # Add completion status
    if 'user' in session:
        lookup = query_db("select solved_challenges from users where username = ?", [session['user']], one=True)
        if lookup is not None and lookup[0] is not None:
            for completed_challenge in lookup[0].split('|'):
                for displayed_challenge in challenges:
                    if str(displayed_challenge["id"]) == completed_challenge:
                        displayed_challenge["completed"] = 1 # The HTML page just checks for the existance of this key-value pair

    return render_template('browse.html', challenges=challenges, categories=categories)

@app.route('/browse', methods=['POST'])
def browse_search():
    name = request.form.get('searchterm')
    cur = query_db('select id, name from challenges where com_flag = 0  or com_flag = 2')
    # Produce an array of hashes that looks something like:
    # [{id->'1', name->'some challenge name'}, {other hash}]  
    challenges = [dict(id=row[0],name=row[1]) for row in cur]
    # Iterate over challenges, and only keep hashes (i.e. challenges) where the names match up
    results = [challenge for challenge in challenges if name.lower() in challenge["name"].lower()]
    # Pass only those on
    return render_template('browse.html', challenges=results, searchterm=request.form.get('searchterm'))
