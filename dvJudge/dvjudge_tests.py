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
        assert 'Invalid username' in rv.data
        rv = self.login('admin', 'defaultx')
        assert 'Invalid password' in rv.data

    def test_messages(self):
        self.login('admin', 'default')
        rv = self.app.post('/add', data=dict(
            title='<Hello>',
            text='<strong>HTML</strong> allowed here'
        ), follow_redirects=True)
        assert 'No entries here so far' not in rv.data
        assert '&lt;Hello&gt;' in rv.data
        assert '<strong>HTML</strong> allowed here' in rv.data

    # test invalid code causes error
    def test_problem1_compile_error(self):
        self.login('admin', 'default')
        rv = self.app.post('/upload_code', data=dict(text='sdafjlkajsdflkasdflkj'))
        assert 'COMPILE ERROR:' in rv.data
        assert 'WRONG ANSWER!' not in rv.data
        assert 'SOLVED!' not in rv.data

    def test_problem1_right_answer(self):
        self.login('admin', 'default')
        rv = self.app.post('/upload_code', data=dict(text=
             """#include <stdio.h>
                #include <stdlib.h>

                int main (void) {
                    printf ("1 2 3 4 5");
                    return 0;
                }"""))
        assert 'COMPILE ERROR:' not in rv.data
        assert 'WRONG ANSWER!' not in rv.data
        assert 'SOLVED!' in rv.data

    def test_problem1_wrong_answer(self):
        self.login('admin', 'default')
        rv = self.app.post('/upload_code', data=dict(text=
             """#include <stdio.h>
                #include <stdlib.h>

                int main (void) {
                    printf ("bacon pancakes");
                    return 0;
                }"""))
        assert 'COMPILE ERROR:' not in rv.data
        assert 'WRONG ANSWER!' in rv.data
        assert 'SOLVED!' not in rv.data

if __name__ == '__main__':
    unittest.main()
