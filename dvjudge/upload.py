from flask import render_template, request, session, abort, g, flash
from dvjudge import app
from core import query_db

# For Uploading challenges
@app.route('/community/upload', methods=['GET', 'POST'])
def upload():
    #if 'logged_in' not in session or session['logged_in'] == False:
    #    abort(401)
    
    # Someone is trying to submit a new challenge
    if request.method == 'POST':
        challenge_name  = request.form.get('challenge_name')
        description     = request.form.get('description')
        input_          = request.form.get('input_')
        output_         = request.form.get('output_')
        tests           = request.form.get('tests')
        input_desc      = request.form.get('input_desc')
        output_desc     = request.form.get('output_desc')

        # Check if the challenge_name already exists in the db
        cur = query_db('select * from challenges where name = ?', [challenge_name], one=True)
        if cur is None:
            add_challenge (challenge_name, description, input_, output_, tests,input_desc, output_desc) 
            flash ("challenge added successfully")
        # If the challenge_name is not fresh, leave the user's details in the page
        else:
            flash ("There is already a challenge with that name")
            render_template('upload_challenge.html', challenge_name=challenge_name, description=description, input_=input_,
                            output_=output_, tests=tests, input_desc=input_desc, output_desc=output_desc)

    return render_template('upload_challenge.html') 

def add_challenge(challenge_name, description, input_, output_, tests,input_desc, output_desc): 
    g.db.execute ("""insert into challenges (name,description,input,output,sample_tests,input_desc,output_desc,com_flag)
                    values (?, ?, ?, ?, ?, ?, ?, 1)""", [challenge_name, description, input_, output_, tests, input_desc, output_desc])
    g.db.commit()
