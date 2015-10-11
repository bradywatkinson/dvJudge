from flask import render_template, session, request, abort, g
from dvjudge import app
from core import query_db, update_db
from comments import get_comments, post_comment

@app.route('/profile/<userid>', methods=['GET'])
def profile(userid):
    cur = query_db('select * from users where name = ?', [userid], one=True)
    if cur is not None:
        user_id  = cur[0]
    return render_template('profile.html')