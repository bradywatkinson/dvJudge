from flask import render_template, session, request, flash, url_for, redirect, abort
from dvjudge import app
from core import query_db, update_db
import subprocess
import os.path
import random
import re
import json

path = '/test/tmp/'
chroot = '/tmp/'
@app.route('/submit', methods=['POST'])
def submit_specific_challenge():
    
    skip = False 
    language = request.form.get('language')
    #if user is logged in the compiled file will be under the username
    if 'user' in session:
        username = session['user']
        user_id = query_db('select id from users where username = ?',[username], one=True)[0]
    else:
        username = 'default'
        skip = True

    #do database stuff
    challenge_id = request.args.get('challenge_id')
    cur = query_db('select * from challenges where id = ?', [challenge_id], one=True)
    
    if cur is not None:
        challenge_id  = cur[0]
        name        = cur[1]
        description = cur[2]
        input_tests = cur[3]
        expected_output = cur[4]
        sample_tests= cur[5]
        input_desc  = cur[6]
        output_desc = cur[7]

    else:
        abort(404)
    
    challenge_info = {'challenge_id': challenge_id, 'name': name, 'description': description, 'sample_tests': sample_tests, 'input_desc': input_desc, 'output_desc': output_desc}
     # get the code from the form
    code = request.form['editor']
    session['code'] = code
    session['language'] = language
    # create a directory for current submission
    directory = subprocess.Popen(['mkdir', path + username], stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
    directory.wait()
    if language == 'C':
        result = run_c(code=code, username = username, input_tests = input_tests, expected_output = expected_output)
    elif language == 'C++':
        result = run_c_plus(code=code, username = username, input_tests = input_tests, expected_output = expected_output)
    elif language == 'Python':
        result = run_python(code=code, username = username, input_tests = input_tests, expected_output = expected_output)
    elif language == 'Java':
        result = run_java(code=code, username = username, input_tests = input_tests, expected_output = expected_output)
    else:
        result = {'output': 'Unknown language', 'status':'Error'}
    # if not a default user, the one that is just trying out the website

    new_solved_challenges = ""
    if not skip:
        update_db("insert into submissions (user_id, challenge_id, status, status_info, language, code) values (?, ?, ?, ?, ?, ?)",
            [user_id,challenge_id,result['status'],result['output'],language,code])
        # Check to see if the user has completed this challenge
        lookup = query_db("select solved_challenges from users where id = ?", [user_id], one=True)
        done = False
        if lookup is not None and lookup[0] is not None:
            new_solved_challenges = lookup[0]
            for challenge_done in lookup[0].split('|'):
                if int(challenge_done) == challenge_id:
                    done = True
                    break

        # If they haven't done it before, append it to their done list
        if done == False:
            if new_solved_challenges == "":
                new_solved_challenges = challenge_info["challenge_id"]
            else:
                new_solved_challenges += "|" + str(challenge_info["challenge_id"])

            update_db("update users set solved_challenges = ? where id = ?", [new_solved_challenges, user_id])
    #clean up
    subprocess.Popen(['rm', '-rf', path + username], stdout=subprocess.PIPE, stderr=subprocess.STDOUT)   
    if len(result['output']) > 2069:
        result['output'] = result['output'][:2069] 
    session['output'] = result['output']
    return redirect(url_for('browse_specific_challenge', challenge_name=name))


def run_c(code, username, input_tests, expected_output):
    #open a file to dump code for submission submission
    submission = open(path+username+'/'+ username +'.c','w')
    submission.write(code)
    submission.close()
    #compile the code with gcc
    compiled = subprocess.Popen(['sudo','chroot','/test/','gcc', '-o', chroot+username+'/'+ username , chroot+username+'/'+ username +'.c'], stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
    compiled.wait()
    
    #if the file has compiled run it otherwise display the warning
    if os.path.isfile(path+username+'/'+ username):
        status = 'Accepted'
        output = "All tests passed. "
        # run with tests
        tests = input_tests.split('|')
        outputs = expected_output.split('|')
        for test in tests:
            #output = output+ "Testing "+test+"\n"
            #include timeout for tjandra
            run = subprocess.Popen(['sudo','chroot','/test/','timeout','5s',chroot+username+'/'+ username], stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
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
        error_warning = re.sub(chroot+username+"/"+username, "program", error_warning)
        output='Error message: '+ error_warning+ "\n"
        status = 'Compile Error'

    return {'output': output, 'status':status}



def run_java(code, username, input_tests, expected_output):

    pattern = re.compile('\s*public\s*class\s*(\w+)')
    m = pattern.search(code)
    if(m):
        class_name = m.group(1)
    else:
        output = "No public class found"
        status = 'Compile Error'
        return {'output': output, 'status':status}

    #open a file to dump code for submission submission
    submission = open(path+username+'/'+ class_name +'.java','w')
    submission.write(code)
    submission.close()

    #compile the code with gcc
    compiled = subprocess.Popen(['sudo','chroot','/test/','javac', chroot+username+'/'+ class_name+'.java'], stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
    compiled.wait()

    #if the file has compiled run it otherwise display the warning
    if os.path.isfile(path+username+'/'+ class_name+'.class'):
        status = 'Accepted'
        output = "All tests passed. "
        # run with tests
        tests = input_tests.split('|')
        outputs = expected_output.split('|')
        for test in tests:
            #output = output+ "Testing "+test+"\n"
            #include timeout for tjandra
            run = subprocess.Popen(['sudo','chroot','/test/','timeout','5s','java','-cp',chroot+username+'/',class_name], stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
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
        error_warning = re.sub(chroot+username+"/"+username, "program", error_warning)
        output='Error message: '+ error_warning+ "\n"
        status = 'Compile Error'
    return {'output': output, 'status':status}

def run_c_plus(code, username, input_tests, expected_output):
    #open a file to dump code for submission submission
    submission = open(path + username+'/'+ username +'.cpp','w')
    submission.write(code)
    submission.close()

    #compile the code with gcc
    compiled = subprocess.Popen(['sudo','chroot','/test/','g++', '-o', chroot+username+'/'+ username , chroot+username+'/'+ username +'.cpp'], stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
    compiled.wait()

    #if the file has compiled run it otherwise display the warning
    if os.path.isfile(path+username+'/'+ username):
        status = 'Accepted'
        output = "All tests passed. "
        # run with tests
        tests = input_tests.split('|')
        outputs = expected_output.split('|')
        for test in tests:
            #output = output+ "Testing "+test+"\n"
            #include timeout for tjandra
            run = subprocess.Popen(['sudo','chroot','/test/','timeout','1s',chroot+username+'/'+ username], stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
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
        error_warning = re.sub(chroot+username+"/"+username, "program", error_warning)
        output='Error message: '+ error_warning+ "\n"
        status = 'Compile Error'

    return {'output': output, 'status':status}

def run_python(code, username, input_tests, expected_output):
 #open a file to dump code for submission submission

    submission = open(path+username+'/'+ username +'.py','w')
    submission.write(code)
    submission.close()

    #if the file has compiled run it otherwise display the warning
    status = 'Accepted'
    output = "All tests passed. "
    # run with tests
    tests = input_tests.split('|')
    outputs = expected_output.split('|')
    for test in tests:
        #output = output+ "Testing "+test+"\n"
        #include timeout for tjandra
        run = subprocess.Popen(['sudo','chroot','/test/','timeout','1s','python',chroot+username+'/'+ username+'.py'], stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
        #run = subprocess.Popen('./submissions/submission', stdin=test, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
        prog_output = run.communicate(test)[0]
        run.wait()
        # the number of inputs must correspond to the number of outputs in the database
        #otherwise an error will occur 
        expected = outputs.pop(0)
        expected = " ".join(expected.split())
        prog_output = " ".join(prog_output.split())
        if prog_output != expected:
            prog_output = re.sub(chroot+username+"/"+username, "program", prog_output)
            if 'Traceback' in prog_output or 'SyntaxError' in prog_output or 'IndentationError' in prog_output:
                output = prog_output
                status = 'Compile Error'
                break
            else:
                output = "Test failed.\nProvided input: " + test +"\n"+"Expected output: "+ expected+"\n"+\
                "Program output:" + prog_output
                status = 'Incorrect'
                break

    return {'output': output, 'status':status}
