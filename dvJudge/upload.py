from flask import render_template, request, session, abort, g, flash
from dvjudge import app

# For Uploading problems
@app.route('/upload', methods=['GET', 'POST'])
def upload():
    if 'logged_in' not in session or session['logged_in'] == False:
        abort(401)
    
    # Someone is trying to submit a new problem
    if request.method == 'POST':
        challenge_name  = request.form.get('challenge_name')
        description     = request.form.get('description')
        input_          = request.form.get('input_')
        output_         = request.form.get('output_')
        tests           = request.form.get('tests')
        input_desc      = request.form.get('input_desc')
        output_desc     = request.form.get('output_desc')

        add_problem (challenge_name, description, input_, output_, tests,input_desc, output_desc) 
        flash ("Problem added successfully")

    return render_template('upload_problem.html') 

def add_problem(challenge_name, description, input_, output_, tests,input_desc, output_desc): 
    g.db.execute ("""insert into challenges (name,description,input,output,sample_tests,input_desc,output_desc)
                    values (?, ?, ?, ?, ?, ?, ?)""", [challenge_name, description, input_, output_, tests, input_desc, output_desc])
    g.db.commit()
