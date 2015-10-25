from flask import render_template, session, request, abort, g
from dvjudge import app
from core import query_db, update_db
from comments import get_comments, post_comment

@app.route('/browse', methods=['GET'])
def browse():
    vals = do_browse(com=False)
    return render_template('browse.html', challenges=vals[0], categories=vals[1], com_flag=False)

def do_browse(com=False):
    if com is False:
        # com_flag of 2 signfies admin chosen challenges that can be attempted by anyone
        cur = query_db('select id, name, submitter_id from challenges where com_flag = 0 or com_flag = 2')
    else:
        cur = query_db('select id, name, submitter_id from challenges where com_flag = 1')

    challenges = [dict(id=row[0],name=row[1],submitter_id=row[2]) for row in cur]

    # Retrieve category names
    cur = query_db('select name from categories');
    if cur:
        categories = [dict(name=row[0]) for row in cur]

    # Add completion status
    if 'user' in session:
        lookup = query_db("select solved_challenges from users where username = ?", [session['user']], one=True)
        if lookup is not None and lookup[0] is not None:
            for completed_challenge in lookup[0].split('|'):
                for displayed_challenge in challenges:
                    if str(displayed_challenge["id"]) == completed_challenge:
                        displayed_challenge["completed"] = 1 # The HTML page just checks for the existance of this key-value pair

    # Convert user_ids to usernames
    for challenge in challenges:
        lookup = query_db("select username from users where id = ?", [challenge["submitter_id"]], one=True)
        if lookup is not None:
            challenge["submitter_id"] = lookup[0]
        else:
            challenge["submitter_id"] = "DvJudge"

    return (challenges, categories)
    # if com is False:
    #     return render_template('browse.html', challenges=challenges, categories=categories, com_flag=True)
    # return render_template('browse.html', challenges=challenges, categories=categories, com_flag=False)

@app.route('/browse', methods=['POST'])
def browse_post():
    vals = do_browse_post(com=False)
    return render_template('browse.html', challenges=vals[0], searchterm=vals[1], categories=vals[2], no_completed=vals[3], com_flag=False)
    # return render_template('browse.html', challenges=vals[0], categories=vals[1], com_flag=False)
    # return render_template('browse.html', challenges=challenges, searchterm=None, categories=categories, no_completed=None, com_flag=False)

def do_browse_post(com=False):
    # User is searching
    if request.form.get('searchterm') is not None: # Search passes a search term
        name = request.form.get('searchterm')
        if com is False:
            cur = query_db('select id, name, submitter_id from challenges where com_flag = 0 or com_flag = 2')
        else:
            cur = query_db('select id, name, submitter_id from challenges where com_flag = 1')
        # Produce an array of hashes that looks something like:
        # [{id->'1', name->'some challenge name'}, {other hash}]  
        challenges = [dict(id=row[0],name=row[1],submitter_id=row[2]) for row in cur]
        # Iterate over challenges, and only keep hashes (i.e. challenges) where the names match up
        results = [challenge for challenge in challenges if name.lower() in challenge["name"].lower()]

        # Add completion status
        if 'user' in session:
            lookup = query_db("select solved_challenges from users where username = ?", [session['user']], one=True)
            if lookup is not None and lookup[0] is not None:
                for completed_challenge in lookup[0].split('|'):
                    for displayed_challenge in challenges:
                        if str(displayed_challenge["id"]) == completed_challenge:
                            displayed_challenge["completed"] = 1 # The HTML page just checks for the existance of this key-value pair
        
        # Convert user_ids to usernames
        for challenge in challenges:
            lookup = query_db("select username from users where id = ?", [challenge["submitter_id"]], one=True)
            if lookup is not None:
                challenge["submitter_id"] = lookup[0]
            else:
                challenge["submitter_id"] = "DvJudge"

            
        cur = query_db('select name from categories');
        if cur:
            categories = [dict(name=row[0]) for row in cur]
        # Pass only those on
        return (results, request.form.get('searchterm'), categories, None)

    # Admin request to move challenges
    elif request.form.get('remove') is not None:
        if session['user'] == "admin":
            if com is False:
                cur = query_db('select id, name from challenges where com_flag = 0 or com_flag = 2')
            else:
                cur = query_db('select id, name from challenges where com_flag = 1')
            # Produce an array of hashes that looks something like:
            # [{id->'1', name->'some challenge name'}, {other hash}]  
            challenges = [dict(id=row[0],name=row[1]) for row in cur]
            cur = query_db('select name from categories');
            if cur:
                categories = [dict(name=row[0]) for row in cur]

            for challenge in challenges:
                move_name = request.form.get(challenge['name'])
                if move_name:
                    move = "update challenges set com_flag=1 where name=?;"
                    update_db(move, [challenge['name']])
            if com is False:
                cur = query_db('select id, name from challenges where com_flag = 0 or com_flag = 2')
            else:
                cur = query_db('select id, name from challenges where com_flag = 1')
            challenges = [dict(id=row[0],name=row[1]) for row in cur]
            return (challenges, None, categories, None)

    # Admin request to delete challenge
    elif request.form.get('delete_chal') is not None:
        if session['user'] == "admin":
            update_db('delete from challenges where name=?',[request.form.get('delete_chal')])
            if com is False:
                cur = query_db('select id, name from challenges where com_flag = 0 or com_flag = 2')
            else:
                cur = query_db('select id, name from challenges where com_flag = 1')
            # Produce an array of hashes that looks something like:
            # [{id->'1', name->'some challenge name'}, {other hash}]  
            challenges = [dict(id=row[0],name=row[1]) for row in cur]
            cur = query_db('select name from categories');
            if cur:
                categories = [dict(name=row[0]) for row in cur]

            return (challenges, None, categories, None)

    else: # If there's no searchterm and we get a post, it's probably filtering.
        
        # Retrieve category names
        cur = query_db('select name from categories');
        categories = ""
        if cur:
            categories = [dict(name=row[0]) for row in cur]
        else:
            categories = None  

        # Set categories
        matching_problems = []
        
        # Check Completed filter
        no_completed = False
        if request.form.get("no_completed") is not None:
            no_completed = True

        # Check the ret of the filters, Figure out which ones were set, and keep them set
        no_filters = True
        for category in categories:
            if request.form.get(category["name"]) is not None:
                no_filters = False
                category["checked"] = True
                # Look it up in the DB to get problems in this category
                cur = query_db('select challenges from categories where name = ?', [category["name"]], one=True)
                if cur is not None:
                    for category_problem in cur[0].split('|'):
                        if category_problem != "" and int(category_problem) not in matching_problems:
                            # Remember all the problems that match any filter
                            matching_problems.append(int(category_problem))
                else:
                    abort(500)

        # Now pull all the problems and only keep matching_problems
        if com is False:
            cur = query_db('select id, name, submitter_id from challenges where com_flag = 0 or com_flag = 2')
        else:
            cur = query_db('select id, name, submitter_id from challenges where com_flag = 1')
        # Produce an array of hashes that looks something like:
        # [{id->'1', name->'some challenge name'}, {other hash}]  
        challenges = [dict(id=row[0],name=row[1],submitter_id=row[2]) for row in cur]

        # List comprehension, for each item in challenges, only keep ones that are in the matching_problems set
        if no_filters == False:
            challenges = [x for x in challenges if x["id"] in matching_problems]
        
        # If completed is turned on, we need to remove any matching_problems that are complete
        # Add completion status
        if no_completed == True and 'user' in session:
            lookup = query_db("select solved_challenges from users where username = ?", [session['user']], one=True)
            if lookup is not None and lookup[0] is not None:
                # List comprehension: Matching problems only
                challenges = [x for x in challenges if str(x["id"]) not in lookup[0].split('|')] 
        
        # Convert user_ids to usernames
        for challenge in challenges:
            lookup = query_db("select username from users where id = ?", [challenge["submitter_id"]], one=True)
            if lookup is not None:
                challenge["submitter_id"] = lookup[0]
            else:
                challenge["submitter_id"] = "DvJudge"

        # Also figure out what to put in the completed column for the page, for the displayed problems
        if 'user' in session:
            lookup = query_db("select solved_challenges from users where username = ?", [session['user']], one=True)
            if lookup is not None and lookup[0] is not None:
                for completed_challenge in lookup[0].split('|'):
                    for displayed_challenge in challenges:
                        if str(displayed_challenge["id"]) == completed_challenge:
                            displayed_challenge["completed"] = 1 # The HTML page just checks for the existance of this key-value pair

        return (challenges, None, categories, None)
        
