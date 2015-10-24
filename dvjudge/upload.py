from flask import render_template, request, session, abort, g, flash
from dvjudge import app
from core import query_db, update_db
import re

# For Uploading challenges
@app.route('/community/upload', methods=['GET', 'POST'])
def upload():
    # Retrieve category names
    cur = query_db('select name from categories');
    if cur:
        categories = [dict(name=row[0]) for row in cur]

    # Initialise alert flags
    flags = {}

    # Someone is trying to submit a new challenge
    if request.method == 'POST':
        challenge_name  = request.form.get('challenge_name')
        description     = request.form.get('description')
        input_          = request.form.get('input_')
        output_         = request.form.get('output_')
        tests           = request.form.get('tests')
        input_desc      = request.form.get('input_desc')
        output_desc     = request.form.get('output_desc')

        flags['empty'] = False
        flags['length'] = False
        flags['special']  = False
        flags['conflict'] = False
        flags['success'] = False
        flags['inempty'] = False
        flags['outempty'] = False

        # Check if challenge_name is empty
        temp = re.sub('[\s+]', '', challenge_name)
        in_temp = re.sub('[\s+]', '', input_)
        out_temp = re.sub('[\s+]', '', output_)
        if not challenge_name or not temp:
            flags['empty'] = True
        elif len(challenge_name) > 70:
            flags['length'] = True
        elif not whitelist(challenge_name):
            flags['special']  = True
        elif not input_ or not in_temp:
            flags['inempty'] = True
        elif not output_ or not out_temp:
            flags['outempty'] = True

        if flags['empty'] or flags['length'] or flags['special'] or flags['inempty'] or flags['outempty']:
            return render_template('upload_challenge.html', challenge_name=challenge_name, description=description, input_=input_,
                output_=output_, tests=tests, input_desc=input_desc, output_desc=output_desc, categories=categories, flags=flags)
        
        # Check if the challenge_name already exists in the db
        cur = query_db('select * from challenges where name = ?', [challenge_name], one=True)
        if cur is None:
            add_challenge (challenge_name, description, input_, output_, tests,input_desc, output_desc) 
            # Get new challenge instance
            cur = query_db('select * from challenges where name = ?', [challenge_name], one=True)
            # Check if adding to a category
            if cur is not None:
                for category in categories:
                    category_name = request.form.get(category['name'])
                    if category_name:
                        cur2 = query_db('select * from categories where name = ?', [category_name], one=True)
                        if cur2 is not None:
                            challenge_ids = cur2[1]
                            if challenge_ids:
                                challenge_ids += "|" + str(cur[0])
                            else:
                                challenge_ids = str(cur[0])

                        new_chal = "update categories set challenges=? where name=?;"
                        update_db(new_chal, [challenge_ids,category_name])

            flags['success'] = True
            return render_template('upload_challenge.html', categories=categories, flags=flags)

        # If the challenge_name is not fresh, leave the user's details in the page
        else:
            flags['conflict'] = True
            render_template('upload_challenge.html', challenge_name=challenge_name, description=description, input_=input_,
                output_=output_, tests=tests, input_desc=input_desc, output_desc=output_desc, categories=categories, flags=flags)

    return render_template('upload_challenge.html', categories=categories, flags=flags) 

def add_challenge(challenge_name, description, input_, output_, tests,input_desc, output_desc): 
    g.db.execute ("""insert into challenges (name,description,input,output,sample_tests,input_desc,output_desc,com_flag)
                    values (?, ?, ?, ?, ?, ?, ?, 1)""", [challenge_name, description, input_, output_, tests, input_desc, output_desc])
    g.db.commit()


def whitelist(strg):
    temp = re.sub('[\s+]', '', strg)
    temp = re.sub('[\w+]', '', temp)
    return not re.search('[^\-\*\^\.\%\:\;\&\#]', temp)
