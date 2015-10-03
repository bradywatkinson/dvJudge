from flask import render_template, session, request, flash, url_for, redirect, abort
from dvjudge import app
from core import query_db, insert_db
import subprocess
import os.path
import random
@app.route('/submit', methods=['POST'])
def submit_specific_problem():
    skip = False
    #if user is logged in the compiled file will be under the username
    if 'user' in session:
        username = session['user']
        user_id = query_db('select id from users where username = ?',[username], one=True)[0]
    else:
        username = 'default'
        skip = True

    #do database stuff
    problem_id = request.args.get('problem_id')
    cur = query_db('select * from challenges where id = ?', [problem_id], one=True)
    if cur is not None:
        problem_id  = cur[0]
        name        = cur[1]
        description = cur[2]
        input_tests = cur[3]
        expected_output = cur[4]
        sample_tests= cur[5]
        input_desc  = cur[6]
        output_desc = cur[7]

    else:
        abort(404)
    problem_info = {'problem_id': problem_id, 'name': name, 'description': description, 'sample_tests': sample_tests, 'input_desc': input_desc, 'output_desc': output_desc}
    

    # get the code from the form
    code = request.form['text']
    # create a directory for current submission
    directory = subprocess.Popen(['mkdir', username], stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
    directory.wait()
    #open a file to dump code for submission submission
    submission = open('./'+username+'/'+ username +'.c','w')
    submission.write(code)
    submission.close()

    #compile the code with gcc
    compiled = subprocess.Popen(['gcc', '-o', './'+username+'/'+ username , './'+username+'/'+ username +'.c'], stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
    compiled.wait()

    #if the file has compiled run it otherwise display the warning
    if os.path.isfile('./'+username+'/'+ username):
        status = 'Accepted'
        output = "All tests passed. "
        # run with tests
        tests = input_tests.split('|')
        outputs = expected_output.split('|')
        for test in tests:
            #output = output+ "Testing "+test+"\n"
            #include timeout for tjandra
            run = subprocess.Popen(['gtimeout','5s','./'+username+'/'+ username], stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
            #run = subprocess.Popen('./submissions/submission', stdin=test, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)


            prog_output = run.communicate(test)[0]
            # the number of inputs must correspond to the number of outputs in the database
            #otherwise an error will occur 
            expected = outputs.pop(0)
            expected = " ".join(expected.split())
            prog_output = " ".join(prog_output.split())
            if prog_output != expected:
                output = "Test failed.\nProvided input: " + test +"\n"+"Expected output: "+ expected+"\n"+\
                 "Program output:" + prog_output
                status = 'Incorrect'
                break;
       
    else: 
        error_warning = compiled.communicate()[0]
        output='Error message: '+ error_warning+ "\n"
        status = 'Compile Error'

    # if not a default user, the one that is just trying out the website
    if not skip:
        insert_db("insert into submissions (user_id, challenge_id, status, status_info)\
    values (?, ?, ?, ?);",[user_id,problem_id,status,output])

    #clean up
    subprocess.Popen(['rm', '-rf', username], stdout=subprocess.PIPE, stderr=subprocess.STDOUT)   
    session['output'] = output
    session['code'] = code
    return redirect(url_for('browse_specific_problem', problem_name=name))
