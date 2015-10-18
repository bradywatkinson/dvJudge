from core import query_db
from flask import g


#this function takes the problem_id as input and returns the comments as an object array
#the object array has this prototype {username, comment, post_time, upvotes, downvotes}
def get_comments(problem_id):
	cur = g.db.cursor()
	cur.execute('select username, comment, post_time from challenge_comments where challenge_id=?', [str(problem_id)])
	comments = [dict(username=row[0],comment=row[1], post_time=row[2]) for row in cur]
	return comments

#this function takes the username, challenge_id and comment and commits it to the database
def post_comment(username, challenge_id, comment):
	g.db.execute("insert into challenge_comments (username, challenge_id, comment) values (?, ?, ?)", [username, challenge_id, comment])
	g.db.commit()

#same as get_comments() but gets comments for forum pages
def get_forum_comments(forum_id):
	cur = g.db.cursor()
	cur.execute('select username, comment, post_time from forum_comment where forum_page=?', [str(forum_id)])
	comments = [dict(username=row[0],comment=row[1], post_time=row[2]) for row in cur]
	return comments

def post_forum_comment(username, forum_id, comment):
	g.db.execute("insert into forum_comment (username, forum_page, comment) values (?, ?, ?)", [username, forum_id, comment])
	g.db.commit()