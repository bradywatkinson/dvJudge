from flask import render_template, request
from dvjudge import app
from core import query_db

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
