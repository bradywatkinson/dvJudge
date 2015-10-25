import zipfile


from dvjudge import init_db, populate_db 
init_db()
populate_db()
with zipfile.ZipFile('profile_pics.zip', "r") as z:
    z.extractall("")
