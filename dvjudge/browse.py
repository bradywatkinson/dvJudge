from flask import render_template, session, request, abort, g
from dvjudge import app
from core import query_db, update_db
from comments import get_comments, post_comment

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
    # [{id->'1', name->'some challenge name'}, {other hash}]  
    challenges = [dict(id=row[0],name=row[1]) for row in cur]
    # Iterate over challenges, and only keep hashes (i.e. challenges) where the names match up
    results = [challenge for challenge in challenges if name.lower() in challenge["name"].lower()]
    # Pass only those on
    return render_template('browse.html', challenges=results, searchterm=request.form.get('searchterm'))


@app.route('/test', methods=['POST'])
def test():
    name = request.form.get('del')
    return "Hello" + name