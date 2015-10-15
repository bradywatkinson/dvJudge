from flask import render_template, session, request, abort, g
from dvjudge import app
from core import query_db, update_db
import re, random

@app.route('/playlists', methods=['GET', 'POST'])
def show_playlists():
    if 'user' in session:
        username = session['user']
        # Convert user session to user ID
        cur = query_db('select id from users where username = ?', [username], one=True)
        if cur is not None:
            owner_id = str(cur[0])
            # Check if selected 'Delete Playlist'
            del_name = request.form.get('delete_list')
            if del_name:
                update_db('delete from playlists where owner_id=? and name=?',[owner_id, del_name])

            # Retrieve the playlists available to this user
            cur = query_db('select * from playlists where owner_id = ?', [cur[0]])
                
            # Build a dictionary to pass to the page later
            # Dictionary contains playlist name, id, and which challenges belong to it
            playlists = [dict(id=row[0],name=row[1],challenges=row[3]) for row in cur]
            if playlists:
                selected_name = request.form.get('selected_name')
                selection = playlists[0]
                if selected_name is not None:
                    for play in playlists:
                        if play['name'] == selected_name:
                            selection = play


                cur = query_db('select id, name from challenges')
                # Produce an array of hashes that looks something like:
                # [{id->'1', name->'some challenge name'}, {other hash}]  
                challenges = [dict(id=row[0],name=row[1]) for row in cur]
                challenge_list = []
                # Determine whether Submit Changes was pressed
                to_reorder = request.form.get('reorder')
                if to_reorder:
                    reorder_entry = {}
                    # Match each challenge to their new order
                    for challenge in challenges:
                        if request.form.get(challenge['name']):
                            chal_order = int(request.form.get(challenge['name']))
                            chal_id = int(challenge['id'])
                            reorder_entry[chal_order] = chal_id

                    # Generate an order string to insert into the database
                    new_order = ""
                    for key in reorder_entry:
                        if not new_order:
                            new_order = str(reorder_entry[key])
                        else:
                            new_order += "|" + str(reorder_entry[key])

                    reorder_str = "update playlists set challenges=? where name=? and owner_id=?;"
                    update_db(reorder_str, [new_order,selection['name'],owner_id])
                    challenge_ids = new_order
                else:
                    challenge_ids = selection['challenges']

                if challenge_ids:
                    # Obtain a list of in order challenge ids for a playlist
                    id_list = [int(s) for s in challenge_ids.split('|')]

                    for id in id_list:
                        challenge_list.append(challenges[id-1])
            else:
                playlists = None
                selection = None
                challenge_list = None

            # Passing playlists.html all the playilst info in a hash
            return render_template('playlists.html', playlists=playlists,
                        selection=selection, challenge_list=challenge_list)
        else:
            abort(401)
    else:
        abort(401)

@app.route('/playlists/<playlist_id>', methods=['GET'])
def show_playlist_challenges(playlist_id):
    # Retrieve the requested playlist
    cur = query_db('select * from playlists where id = ?', [playlist_id], one=True)
    if cur is not None:
        challenge_ids = cur[3]
        cur = query_db('select id, name from challenges')
        # Produce an array of hashes that looks something like:
        # [{id->'1', name->'some challenge name'}, {other hash}]
        all_challenges = [dict(id=row[0],name=row[1]) for row in cur]  
        challenges = []
        if challenge_ids:
            # Obtain a list of in order challenge ids for a playlist
            id_list = [int(s) for s in challenge_ids.split('|')]
            for id in id_list:
                for challenge in all_challenges:
                    if challenge['id'] == id:
                        challenges.append(dict(id=challenge['id'],name=challenge['name']))
                        break

        return render_template('browse.html', challenges=challenges)

    else:
        abort(404)


@app.route('/new_playlist', methods=['GET'])
def show_playlist_form():
    if 'user' in session:
        cur = query_db('select id, name from challenges')
        challenges = [dict(id=row[0],name=row[1]) for row in cur]
        flags= {}
        play_id = None
        return render_template('new_playlist.html', challenges=challenges, flags=flags, play_id=play_id)
    else:
        abort(401)

@app.route('/new_playlist', methods=['POST'])
def create_new_playlist():
    if 'user' in session:
        username = session['user']
        cur = query_db('select id from users where username = ?', [username], one=True)
        if cur is not None:
            user_id = cur[0]
            # Set fields to check to false and grab playlist name
            flags = {'no_name':False, 'conflict_name':False, 'new_name':None}
            playlist_name = request.form.get('playlist_name')
            temp = re.sub('[\s+]', '', playlist_name)
            play_id = None

            cur = query_db('select id, name from challenges')
            challenges = [dict(id=row[0],name=row[1]) for row in cur]

            # If invalid playlist name, flash an alert
            if not request.form.get('playlist_name') or not temp:
                flags['no_name'] = True
            # Insert new playlist into database
            else:
                flags['new_name'] = playlist_name
                cur2 = query_db('select * from playlists where owner_id = ? and name = ?',
                    [user_id, playlist_name], one=True)
                if cur2 is None:
                    play_id = random.randint(0, 1000000)
                    id_check = query_db('select * from playlists where id = ?', [play_id], one=True)
                    while id_check is not None:
                        play_id = random.randint(0, 1000000)
                        id_check = query_db('select * from playlists where id = ?', [play_id], one=True)

                    challenge_ids = ""
                    for challenge in challenges:
                        id = request.form.get(challenge['name'])
                        if id:
                            if not challenge_ids:
                                challenge_ids = str(id)
                            else:
                                challenge_ids += "|" + str(id)
                    g.db.execute('insert into playlists (id, name, owner_id, challenges) values (?, ?, ?, ?)',
                        [play_id, playlist_name, user_id, challenge_ids])
                    g.db.commit()  
                else:
                    flags['conflict_name'] = True  

            return render_template('new_playlist.html', challenges=challenges, flags=flags, play_id=play_id)
        else:
            abort(401)
    else:
        abort(401)
