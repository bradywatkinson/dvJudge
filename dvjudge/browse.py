from flask import render_template, session, request, abort
from dvjudge import app
from core import query_db
from comments import get_comments, post_comment

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

@app.route('/browse/<problem_name>', methods=['GET', 'POST'])
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

    #insert the comments section
    question_comments = get_comments(problem_id)

    return render_template('problem.html', problem_info=problem_info, output=info, code = code, problem_name=problem_name, comments=question_comments)
