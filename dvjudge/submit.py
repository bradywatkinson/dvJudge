from flask import render_template, session, request, flash, url_for, redirect, abort
from dvjudge import app
from core import query_db
import subprocess
import os.path
@app.route('/submit', methods=['POST'])
def submit_specific_problem():
    #flash ("Successfully submitted for problem " + request.args.get('problem_id'))
    #do database stuff
    problem_id = request.args.get('problem_id')
    cur = query_db('select * from challenges where id = ?', [problem_id], one=True)
    if cur is not None:
        name        = cur[1]
        description = cur[2]
        sample_tests= cur[5]
        input_desc  = cur[6]
        output_desc = cur[7]
    else:
        abort(404)
    problem_info = {'problem_id': problem_id, 'name': name, 'description': description, 'sample_tests': sample_tests, 'input_desc': input_desc, 'output_desc': output_desc}
    
    # get the code from the form
    code = request.form['editor']
    # create a directory for current submission
    directory = subprocess.Popen(['mkdir', 'submissions'], stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
    directory.wait()
    #open a file to dump code for submission submission
    submission = open('./submissions/submission.c','w')
    submission.write(code)
    submission.close()

    #compile the code with gcc
    compiled = subprocess.Popen(['gcc', '-o', './submissions/submission', './submissions/submission.c'], stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
    compiled.wait()

    #if the file has compiled run it otherwise display the warning
    if os.path.isfile('./submissions/submission'):
        # run with tests
        # create a fake testfile since we don't have tests now
        create = subprocess.Popen(['mkdir', 'test'], stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
        create = subprocess.Popen(['touch', './test/testfile'], stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
        create.wait()
        test = open('./test/testfile','w')
        test.write("This is a testfile")
        test.close()
        test = open('./test/testfile','r')
        #include timeout for tjandra
        run = subprocess.Popen(['gtimeout','5s','./submissions/submission'], stdin=test, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
        #run = subprocess.Popen('./submissions/submission', stdin=test, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
        test.close()

        output = run.communicate()[0]
        output = 'Program output: '+ output
    else: 
        error_warning = compiled.communicate()[0]
        output='Error message: '+ error_warning

    #clean up
    subprocess.Popen(['rm', '-rf', 'submissions'], stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
    subprocess.Popen(['rm', '-rf', 'test'], stdout=subprocess.PIPE, stderr=subprocess.STDOUT)   
    
    output = unicode(output, 'utf-8') 
    session['output'] = output
    session['code'] = code
    return redirect(url_for('browse_specific_problem', problem_name=name))
