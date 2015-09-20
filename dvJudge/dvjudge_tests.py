import os
import dvjudge 
import unittest
import tempfile

class FlaskrTestCase(unittest.TestCase):

    def setUp(self):
        self.db_fd, dvjudge.app.config['DATABASE'] = tempfile.mkstemp()
        dvjudge.app.config['TESTING'] = True
        self.app = dvjudge.app.test_client()
        dvjudge.init_db()
        dvjudge.populate_db()

    def tearDown(self):
        os.close(self.db_fd)
        os.unlink(dvjudge.app.config['DATABASE'])

    def test_empty_db(self):
        rv = self.app.get('/')
        assert 'No entries here so far' in rv.data

    def login(self, username, password):
        return self.app.post('/login', data=dict(
                    username=username,
                    password=password
                    ), follow_redirects=True)

    def logout(self):
        return self.app.get('/logout', follow_redirects=True)

    def test_login_logout(self):
        rv = self.login('admin', 'default')
        assert 'You were logged in' in rv.data
        rv = self.logout()
        assert 'You were logged out' in rv.data
        rv = self.login('adminx', 'default')
        assert "Username and password do not match" in rv.data
        rv = self.login('admin', 'defaultx')
        assert "Username and password do not match" in rv.data

    def test_messages(self):
        self.login('admin', 'default')
        rv = self.app.post('/add', data=dict(
            title='<Hello>',
            text='<strong>HTML</strong> allowed here'
        ), follow_redirects=True)
        assert 'No entries here so far' not in rv.data
        assert '&lt;Hello&gt;' in rv.data
        assert '<strong>HTML</strong> allowed here' in rv.data

    def test_upload_problem(self):
        self.login('admin', 'default')
        rv = self.app.post('/upload', data=dict(
            name='testproblemname',
            description='testproblemdescription'
        ), follow_redirects=True)
        rv = self.app.get('/browse')
        assert ('testproblemname') in rv.data
        assert ('notproblemname') not in rv.data

    def test_submit_solution(self):
        self.login('admin', 'default')
        rv = self.app.post('/upload', data=dict(
            name='problem name test',
            description='this is a problem'
        ), follow_redirects=True)
        
        rv = self.app.get('/browse/4')
        assert ('problem name test') in rv.data
        assert ('this is a problem') in rv.data

if __name__ == '__main__':
    unittest.main()
