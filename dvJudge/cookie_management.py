from flask import g, request
#this file contains all cookie retrieval and setting functions

#returns the session id if true
def is_logged_in():
	session_id = request.cookies.get('dvjudge')
	cursor = g.db.cursor()
	cursor.execute("select user_id from user_sessions where session_id=?", [session_id])
	if cursor.fetchone():
		return True
	else:
		return False

#reads the cookie then queries the database for the username that is held by the session id
#returns username
def get_username():
	session_id = request.cookies.get('dvjudge')
	if not session_id:
		return False
	cursor = g.db.cursor()
	cursor.execute("select user_id from user_sessions where session_id=?", [session_id])
	return cursor.fetchone()