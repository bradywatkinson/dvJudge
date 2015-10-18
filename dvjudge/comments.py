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
	cur.execute('select username, comment, post_time, comment_id from forum_comment where forum_page=?', [str(forum_id)])
	comments = [dict(username=row[0],comment=row[1], post_time=row[2], comment_id=row[3], votes=get_forum_net_votes(row[3])) for row in cur]
	return comments

def get_forum_net_votes(comment_id):
	cur = g.db.cursor()
	cur.execute('select count(*) from comment_upvotes where comment_id=?', [comment_id])
	up = cur.fetchone()

	cur = g.db.cursor()
	cur.execute('select count(*) from comment_downvotes where comment_id=?', [comment_id])
	down = cur.fetchone()

	return up[0] - down[0]

def post_forum_comment(username, forum_id, comment):
	g.db.execute("insert into forum_comment (username, forum_page, comment) values (?, ?, ?)", [username, forum_id, comment])
	g.db.commit()

#if the person hasn't already voted it adds their vote to the database
def comment_upvote(user_id, comment_id):
	#if there is a downvote then delete it
	g.db.execute("delete from comment_downvotes where user_id=? and comment_id=?", [user_id, comment_id])
	#check if there is already an upvote and if there is ignore it
	cur = g.db.cursor()
	cur.execute('select count(*) from comment_upvotes where user_id=? and comment_id=?', [user_id, comment_id])
	num_comments = cur.fetchone()
	if num_comments[0] == 0:
		g.db.execute("insert into comment_upvotes (user_id, comment_id) values (?, ?)", [user_id, comment_id])
		g.db.commit()

#if the person hasn't already voted it adds their vote to the database
def comment_downvote(user_id, comment_id):
	g.db.execute("delete from comment_upvotes where user_id=? and comment_id=?", [user_id, comment_id])

	cur = g.db.cursor()
	cur.execute('select count(*) from comment_downvotes where user_id=? and comment_id=?', [user_id, comment_id])
	num_comments = cur.fetchone()
	if num_comments[0] == 0:
		g.db.execute("insert into comment_downvotes (user_id, comment_id) values (?, ?)", [user_id, comment_id])
		g.db.commit()