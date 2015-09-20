from flask import render_template, request, session, abort, g, flash
from dvjudge import app

# For Uploading problems
@app.route('/upload', methods=['GET', 'POST'])
def upload():
    if 'logged_in' not in session or session['logged_in'] == False:
        abort(401)
    
    # Someone is trying to submit a new problem
    if request.method == 'POST':
        name = request.form.get('name')
        description = request.form.get('description')
        # TODO: Validate?
        add_problem (name, description) 
        flash ("Problem added successfully")

    return render_template('upload_problem.html') 

def add_problem(name, description):
    g.db.execute ("""insert into challenges (name,description,input,output,sample_input,sample_output)
                    values (?, ?, 'test', 'test', null, null)""", [name, description])
    g.db.commit()
