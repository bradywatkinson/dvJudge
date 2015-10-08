import os
from dvjudge import init_db, populate_db
from dvjudge import core
import unittest
import tempfile
import re

class FlaskrTestCase(unittest.TestCase):

    def setUp(self):
        self.db_fd, core.app.config['DATABASE'] = tempfile.mkstemp()
        core.app.config['TESTING'] = True
        self.app = core.app.test_client()
        init_db()
        populate_db()

    def tearDown(self):
        os.close(self.db_fd)
        os.unlink(core.app.config['DATABASE'])

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

    def test_user_signup_works(self):
        self.app.post('/signup')
        rv = self.app.post('/signup', data=dict(
                    username='username',
                    password='password',
                    confirmpassword='password',
                    email='dan@hotmail.com',
                    confirmemail='dan@hotmail.com'
                    ), follow_redirects=True)
        assert 'Username is already taken' not in rv.data
        assert 'Passwords need to be 6 characters or longer' not in rv.data
        assert 'Emails do not match' not in rv.data
        assert 'Passwords do not match' not in rv.data

    def test_user_signup_no_work(self):
        self.app.post('/signup')
        rv = self.app.post('/signup', data=dict(
                    username='admin',
                    password='password',
                    confirmpassword='spassword',
                    email='dan@hotmail.com',
                    confirmemail='dain@hotmail.com'
                    ), follow_redirects=True)
        assert 'Passwords need to be 6 characters or longer' not in rv.data
        assert 'Emails do not match' in rv.data
        assert 'Passwords do not match' in rv.data

    def test_login_landing_page(self):
        rv = self.app.get('/')
        assert ('SIGN UP TODAY') in rv.data
        assert ('textarea') in rv.data
        assert ('VIEW YOUR PROGRESS') not in rv.data
        assert ('Upload Code') not in rv.data
        self.login('admin', 'default')
        rv = self.app.get('/')
        assert ('VIEW YOUR PROGRESS') in rv.data
        assert ('Upload Code') in rv.data
        assert ('textarea') not in rv.data
        assert ('SIGN UP TODAY') not in rv.data

    def test_upload_problem(self):
        self.login('admin', 'default')
        rv = self.app.post('/upload', data=dict(
            challenge_name='testproblemname',
            description='testproblemdescription'
        ), follow_redirects=True)
        rv = self.app.get('/browse')
        assert ('testproblemname') in rv.data
        assert ('notproblemname') not in rv.data
    

    # creates a new challenge and checks that it is
    # browseable. NOTE: this relies on only 2 challenges
    # already in the db
    def test_submit_solution(self):
        self.login('admin', 'default')
        rv = self.app.post('/upload', data=dict(
            challenge_name='problem name test',
            description='this is a problem'
        ), follow_redirects=True)
        
        rv = self.app.get('/browse/problem%20name%20test')
        assert ('problem name test') in rv.data
        assert ('this is a problem') in rv.data

    def test_browse_search(self):
        # Add some problems via upload problem
        self.login('admin', 'default')
        rv = self.app.post('/upload', data=dict(
            challenge_name='1 - Count to N',
            description='testproblemdescription'
        ), follow_redirects=True)
        rv = self.app.post('/upload', data=dict(
            challenge_name='2 - Sum to N',
            description='testproblemdescription'
        ), follow_redirects=True)
        rv = self.app.post('/upload', data=dict(
            challenge_name='3 - Sum to N^2',
            description='testproblemdescription'
        ), follow_redirects=True)
        rv = self.app.post('/upload', data=dict(
            challenge_name='4 - Subtract 5 from N',
            description='testproblemdescription'
        ), follow_redirects=True)
        
        # Now try searching for Subtract 
        rv = self.app.post('/browse', data=dict(
            searchterm='Subtract'
        ), follow_redirects=True)

        assert ('1 - Count to N') not in rv.data
        assert ('2 - Sum to N') not in rv.data
        assert ('4 - Subtract 5 from N') in rv.data
        assert ('3 - Sum to N^2') not in rv.data

        # Now try searching for nothing (i.e. show all)
        rv = self.app.post('/browse', data=dict(
            searchterm=''
        ), follow_redirects=True)

        assert ('1 - Count to N') in rv.data
        assert ('2 - Sum to N') in rv.data
        assert ('3 - Sum to N^2') in rv.data
        assert ('4 - Subtract 5 from N') in rv.data
        
        # Now try searching for special character '^'
        rv = self.app.post('/browse', data=dict(
            searchterm='^'
        ), follow_redirects=True)

        assert ('1 - Count to N') not in rv.data
        assert ('2 - Sum to N') not in rv.data
        assert ('3 - Sum to N^2') in rv.data
        assert ('4 - Subtract 5 from N') not in rv.data
        
        #testing code submission
    def test_c_submission(self):
        self.login('admin','default')
        #submit code with errors
        rv = self.app.post('/submit?problem_id=1',data=dict(
            text="printf",
            language = 'C'
            ),follow_redirects=True)

        assert('error') in rv.data
        assert('printf') in rv.data

        rv = self.app.get('/submissions/4', follow_redirects=True)
        assert('Status: Compile Error') in rv.data

        #submit valid code
        rv = self.app.post('/submit?problem_id=1',data=dict(
            text="int main(){return 0;}",
            language = 'C'
            ),follow_redirects=True)
        assert('Program output') in rv.data

        rv = self.app.get('/submissions/6', follow_redirects=True)
        assert('Status: Incorrect') in rv.data
        #test another challenge for submission
        rv = self.app.post('/submit?problem_id=2',data=dict(
            text="int main(){return 0;}",
            language = 'C'
            ),follow_redirects=True)
        assert('Program output') in rv.data

        rv = self.app.post('/submit?problem_id=2',data=dict(
            text="printf",
            language = 'C'
            ),follow_redirects=True)
        assert('error') in rv.data
        assert('printf') in rv.data

        #passing all the tests
        rv = self.app.post('/submit?problem_id=1',data=dict(
            text='''#include <stdio.h> 
                    int main(){
                        int num; 
                        scanf("%d",&num);
                        for(int i = 0; i < num; i++){ 
                            printf("%d", i+1); 
                            if(i < num-1){
                                printf(" ");
                            }
                        }
                    }''',
            language = 'C'
            ),follow_redirects=True)
        assert("All tests passed") in rv.data

        rv = self.app.post('/submit?problem_id=1',data=dict(
            text='''#include <stdio.h> 
                    int main(){
                        int num; 
                        scanf("%d",&num);
                        for(int i = 0; i < num; i++){ 
                            printf("%d", i+1)
                            if(i < num-1){
                                printf(" ");
                            }
                        }
                    }''',
            language = 'C'
            ),follow_redirects=True)
        assert("Error") in rv.data

        rv = self.app.post('/submit?problem_id=1',data=dict(
            text='''#include <stdio.h> 
                    int main(){
                        int num; 
                        scanf("%d",&num);
                        for(int i = 0; i < num; i++){ 
                            printf("%d", i+1);
                            if(i < num-1){
                                printf("-");
                            }
                        }
                    }''',
            language = 'C'
            ),follow_redirects=True)
        assert("Test failed") in rv.data
        assert("Provided input") in rv.data
        assert("Expected output") in rv.data
        assert("Program output") in rv.data

    def test_java_submission(self):
        self.login('admin','default')

        #all tests passed
        rv = self.app.post('/submit?problem_id=1',data=dict(
            text='''import java.util.Scanner;
                    public class HelloWorld { 
                        public static void main(String[] args) { 
                        Scanner sc = new Scanner(System.in);
                        int max = sc.nextInt();
                        for(int i = 1; i<=max; i++){
                            System.out.print(i+" ");
                        }
                       }
                    }''',
            language = 'Java'
            ),follow_redirects=True)
        assert('All tests passed.') in rv.data
        rv = self.app.get('/submissions/5', follow_redirects=True)
        assert('Accepted') in rv.data

        #output doesn't match
        rv = self.app.post('/submit?problem_id=1',data=dict(
            text='''import java.util.Scanner;
                    public class HelloWorld { 
                        public static void main(String[] args) { 
                        Scanner sc = new Scanner(System.in);
                        int max = sc.nextInt();
                        for(int i = 1; i<max; i++){
                            System.out.print(i+" ");
                        }
                       }
                    }''',
            language = 'Java'
            ),follow_redirects=True)
        assert("Test failed") in rv.data
        assert("Provided input") in rv.data
        assert("Expected output") in rv.data
        assert("Program output") in rv.data
        rv = self.app.get('/submissions/6', follow_redirects=True)
        assert('Status: Incorrect') in rv.data
   
    #test comments and comment submission
    def test_comment_submission(self):
        self.login('dannyeei', 'daniel')
        rv = self.app.get('/browse/Count%20to%20N', follow_redirects=True)
        assert('Hello World!') not in rv.data
        rv = self.app.post('/browse/Count%20to%20N', data=dict(
            comment='Hello World!'))
        assert('Hello World!') in rv.data
        rv = self.app.post('/browse/Count%20to%20N', data=dict(
            comment='New comment'))
        assert('New comment') in rv.data
        assert('Hello World!') in rv.data
        rv = self.app.post('/browse/Count%20to%20N', data=dict(
            comment='Long comment including odd characters: !@#$,.;:'))
        assert('New comment') in rv.data
        assert('Hello World!') in rv.data
        assert('Long comment including odd characters: !@#$,.;:') in rv.data

    def test_python_submission(self):
        self.login('admin','default')

        #all tests passed
        rv = self.app.post('/submit?problem_id=1',data=dict(
            text='''number = raw_input()
                    for num in range(1,int(number)+1):
                        print num,''',
            language = 'Python'
            ),follow_redirects=True)
        assert('IndentationError') in rv.data
        rv = self.app.get('/submissions/5', follow_redirects=True)
        assert('Compile Error') in rv.data


    def test_c_plus_submission(self):
        self.login('admin','default')

        #all tests passed
        rv = self.app.post('/submit?problem_id=2',data=dict(
            text='''#include<iostream>
                    using namespace std;
                    int main()
                    {
                     long int sum=0;
                     int n;
                     cin>>n;
                     for(int num=1;num<=n;num++)
                     {
                      sum=sum+num;
                     }
                     cout<<sum;
                    }''',
            language = 'C++'
            ),follow_redirects=True)
        assert('All tests passed.') in rv.data
        rv = self.app.get('/submissions/5', follow_redirects=True)
        assert('Accepted') in rv.data

    # Test database imported submissions are displaying properly 
    def test_view_all_submissions(self):
        self.login('dannyeei', 'daniel')
        rv = self.app.get('/submissions', follow_redirects=True)
        # Check if we can see our 3 problems that are pre-populated
        assert('Accepted') in rv.data
        assert('Incorrect') in rv.data
        assert('Compile Error') in rv.data
        assert('Something Else') not in rv.data

    # Test database imported specific submission is working as intended
    def test_specific_submission(self):
        self.login('dannyeei', 'daniel')
        rv = self.app.get('/submissions/1', follow_redirects=True)
        assert('Accepted') in rv.data
        assert('This is a status info') in rv.data
        assert('I would have like a compile error or something in here') in rv.data
        assert('Blab blah you failed some testcases man') not in rv.data
        
    # Test a challenge shows the correct "add to playlist" buttons in the dropdown
    def test_add_to_playlist(self):
        self.login('dannyeei', 'daniel')
        rv = self.app.get('/browse/Sum%20to%20N', follow_redirects=True)
        assert("Create a program that prints sum 1..n") in rv.data
        assert("Add to \"my playlist first ever\"") in rv.data
        assert("Add to \"my second playlist ever\"") in rv.data

    # Test creating playlists works
    def test_create_playlist(self):
        self.login('dannyeei', 'daniel')
        rv = self.app.get('/browse/Sum%20to%20N', follow_redirects=True)
        assert("Create a program that prints sum 1..n") in rv.data
        assert("Add to \"my playlist first ever\"") in rv.data
        assert("Add to \"my second playlist ever\"") in rv.data
        assert("Add to \"AUTOMATED TEST\"") not in rv.data

        # Add new playlist
        rv = self.app.post('/new_playlist', data=dict(
                    playlist_name="AUTOMATED TEST",
                    ), follow_redirects=True)

        # Now check we have three now 
        rv = self.app.get('/browse/Sum%20to%20N', follow_redirects=True)
        assert("Create a program that prints sum 1..n") in rv.data
        assert("Add to \"my playlist first ever\"") in rv.data
        assert("Add to \"my second playlist ever\"") in rv.data
        assert("Add to \"AUTOMATED TEST\"") in rv.data

    # Test creating playlists works
    def test_show_playlist(self):
        self.login('dannyeei', 'daniel')
        rv = self.app.get('/playlists', follow_redirects=True)
        # Check dropdown menu is operational
        assert("<option selected>my playlist first ever") in rv.data
        assert("my second playlist ever") in rv.data
        # Check challenges displayed correctly
        assert("Count to N") in rv.data
        assert("Dota 2 is a great game") in rv.data
        assert("Sum to N") not in rv.data
        assert("Valve cant program") not in rv.data
        
        # Change selected playlist to display
        rv = self.app.post('/playlists',data=dict(
                        selected_name = 'my second playlist ever'
                        ), follow_redirects=True)
        # Check dropdown menu is operational
        assert("<option selected>my playlist first ever") not in rv.data
        assert("<option selected>my second playlist ever") in rv.data
        # Check challenges displayed correctly
        assert("Dota 2 is a great game") in rv.data
        assert("Valve cant program") in rv.data
        assert("Count to N") not in rv.data
        assert("Sum to N") not in rv.data

    # Test no playlist page
    def test_no_playlist(self):
        self.login('admin', 'default')
        rv = self.app.get('/playlists', follow_redirects=True)
        # Check dropdown menu is operational
        assert("You have no playlists.") in rv.data
        assert("option") not in rv.data
        assert("table") not in rv.data
        assert("Submit") not in rv.data

    # Test reorder playlist
    def test_reorder_playlist(self):
        self.login('typical', 'typical')
        rv = self.app.get('/playlists', follow_redirects=True)
        assert ("Count to N: 1") in rv.data
        assert ("Sum to N: 2") in rv.data
        assert ("Dota 2 is a great game: 3") in rv.data
        assert ("Valve cant program: 4") in rv.data

        data = {}
        data['Valve cant program'] = "1"
        data['Dota 2 is a great game'] = "2"
        data['Sum to N'] = "3"
        data['Count to N'] = "4"
        data['reorder'] = "Submit Changes"
        data['selected_name'] = "different playlist"

        # Change challenge ordering
        rv = self.app.post('/playlists',data=data, follow_redirects=True)
        assert ("Valve cant program: 1") in rv.data
        assert ("Dota 2 is a great game: 2") in rv.data
        assert ("Sum to N: 3") in rv.data
        assert ("Count to N: 4") in rv.data


if __name__ == '__main__':
    unittest.main()
