from flask import render_template, session, request, abort, g, redirect
from dvjudge import app
from comments import get_forum_comments, post_forum_comment, comment_upvote, comment_downvote
import re

@app.route('/forums-new/<forum_problem>', methods=['GET', 'POST'])
def new_forum(forum_problem):
	error = ""
	if not 'user' in session:
		return forums_browse(forum_problem)
	if request.method == 'POST':
		post_question = request.form['question']
		post_body = request.form['postbody']
		errors = []
		if not post_question:
			errors.append("Please enter a question")
		if len(post_question) < 6:
			errors.append("Your question needs to be longer than 6 characters")
		if len(post_question) > 60:
			errors.append("Your question exceeds the 60 character limit")
		if not post_body:
			errors.append("Please give details on your question")
		if len(post_body) > 400:
			errors.append("Over the 400 character limit for question descriptions")
		if len(post_body) < 12:
			errors.append("Please enter at least a 12 character description")
		if len(errors) != 0:
			return render_template('new_forum.html', error=errors)
		else:
			g.db.execute("insert into forum_page (problem_id, original_poster, post_name, post_body) values (?, ?, ?, ?)", [forum_problem, session['user'], post_question, post_body])
			g.db.commit()
			cur = g.db.cursor()
			cur.execute('select id from forum_page where post_name=?', [post_question])
			row = cur.fetchone()
			return redirect('/forums/%s/%s' % (forum_problem, row[0]))#forums_question(forum_problem, cur.fetchone)

	return render_template('new_forum.html', error=error)

@app.route('/forums/<forum_problem>', methods=['GET'])
def forums_browse(forum_problem):
	cur = g.db.cursor()
	cur.execute('select original_poster, post_name, post_time, id from forum_page where problem_id=?', str(forum_problem))
	forum_posts = {}
	logged_in = False
	if 'user' in session:
		logged_in = True
	if cur.rowcount != 0:
		forum_posts = [dict(username=row[0],post_name=row[1],post_time=row[2],problem_id=row[3]) for row in cur]
	return render_template('forum.html', posts=forum_posts, forum_problem=forum_problem, logged_in=logged_in)

@app.route('/forums/<forum_problem>/<forum_question>/<sign>/<comment_id>')
def forum_comment_vote(forum_problem, forum_question, sign, comment_id):
	if sign == '+':
		comment_upvote(session['user'], comment_id)
	elif sign == '-':
		comment_downvote(session['user'], comment_id)

	#query database for forum post details
	return redirect('/forums/%s/%s' % (forum_problem, forum_question))

@app.route('/forums/<forum_problem>/<forum_question>', methods=['GET', 'POST'])
def forums_question(forum_problem, forum_question):
	error = ""
	if request.method == 'POST':
		if 'user' in session:
			if request.form['comment']:
				comment = request.form['comment']
				post_forum_comment(session['user'], forum_question, comment)
		else:
			error += "You need to be logged in to comment"
	#query database for forum post details
	cur = g.db.cursor()
	cur.execute('select original_poster, post_name, post_body, post_time from forum_page where id=?', [str(forum_question)])
	forum_details = [dict(username=row[0], question=row[1], body=row[2], post_time=row[3]) for row in cur]
	comments = get_forum_comments(forum_question)
	return render_template('forum_question.html', forum_problem=forum_problem, forum_question=forum_question, forum_details=forum_details, comments=comments, error=error)

@app.route('/forums/<forum_problem>', methods=['POST'])
def forums_search(forum_problem=None):
	if 'user' in session:
		logged_in = True
	#check to see if forum_problem was entered 
	if forum_problem == None:
		#search through whole database
		return render_template('forum.html')
	else:
		cur = g.db.cursor()
		cur.execute('select original_poster, post_name, post_time, id, post_body from forum_page where problem_id=?', str(forum_problem))
		if cur.rowcount != 0:
			forum_posts = [dict(username=row[0],post_name=row[1],post_time=row[2],problem_id=row[3],post_body=row[4]) for row in cur]
			searched_posts = []
			for post in forum_posts:
				if re.search(r'%s' % (request.form['forumsearch']), post['post_name']) or re.search(r'%s' % (request.form['forumsearch']), post['post_body']):
					searched_posts.append(post)

		return render_template('forum.html', posts=searched_posts, forum_problem=forum_problem, logged_in=logged_in)
	








