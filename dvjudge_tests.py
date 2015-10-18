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
        rv =  self.app.post('/login_signup_form', data=dict(
                    submit='signin',
                    username=username,
                    password=password,
                    page='show_mainpage'
                    ), follow_redirects=True)
        return rv

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
        self.app.get('/show_mainpage')
        rv = self.app.post('/login_signup_form', data=dict(
                    submit='signup',
                    username='username',
                    password='password',
                    confirmpassword='password',
                    email='dan@hotmail.com',
                    ), follow_redirects=True)
        assert 'Username is already taken' not in rv.data
        assert 'Passwords need to be 6 characters or longer' not in rv.data
        assert 'Emails do not match' not in rv.data
        assert 'Passwords do not match' not in rv.data

    def test_user_signup_no_work(self):
        self.app.get('/show_mainpage')
        rv = self.app.post('/login_signup_form', data=dict(
                    submit='signup',
                    username='admin',
                    password='password',
                    confirmpassword='spassword',
                    email='dan@hotmail.com',
                    ), follow_redirects=True)
        assert 'Passwords need to be 6 characters or longer' not in rv.data

    def test_login_landing_page(self):
        rv = self.app.get('/')
        assert ('textarea') in rv.data
        assert ('VIEW YOUR PROGRESS') not in rv.data
        assert ('Upload Code') not in rv.data
        self.login('admin', 'default')
        rv = self.app.get('/')
        assert ('VIEW YOUR PROGRESS') in rv.data
        assert ('Upload Code') in rv.data
        assert ('SIGN UP TODAY') not in rv.data

    def test_upload_challenge(self):
        self.login('admin', 'default')
        rv = self.app.post('/community/upload', data=dict(
            challenge_name='testchallengename',
            description='testchallengedescription'
        ), follow_redirects=True)
        rv = self.app.get('/community/browse')
        assert ('testchallengename') in rv.data
        assert ('notchallengename') not in rv.data
    

    # creates a new challenge and checks that it is
    # browseable. NOTE: this relies on only 2 challenges
    # already in the db
    def test_submit_solution(self):
        self.login('admin', 'default')
        rv = self.app.post('/community/upload', data=dict(
            challenge_name='challenge name test',
            description='this is a challenge'
        ), follow_redirects=True)
        
        rv = self.app.get('/community/browse/challenge%20name%20test')
        assert ('challenge name test') in rv.data
        assert ('this is a challenge') in rv.data

    def test_browse_search(self):
        # Add some challenges via upload challenge
        self.login('admin', 'default')
        rv = self.app.post('/community/upload', data=dict(
            challenge_name='1 - Count to N',
            description='testchallengedescription'
        ), follow_redirects=True)
        rv = self.app.post('/community/upload', data=dict(
            challenge_name='2 - Sum to N',
            description='testchallengedescription'
        ), follow_redirects=True)
        rv = self.app.post('/community/upload', data=dict(
            challenge_name='3 - Sum to N^2',
            description='testchallengedescription'
        ), follow_redirects=True)
        rv = self.app.post('/community/upload', data=dict(
            challenge_name='4 - Subtract 5 from N',
            description='testchallengedescription'
        ), follow_redirects=True)
        
        # Now try searching for Subtract 
        rv = self.app.post('/community/browse', data=dict(
            searchterm='Subtract'
        ), follow_redirects=True)

        assert ('1 - Count to N') not in rv.data
        assert ('2 - Sum to N') not in rv.data
        assert ('4 - Subtract 5 from N') in rv.data
        assert ('3 - Sum to N^2') not in rv.data

        # Now try searching for nothing (i.e. show all)
        rv = self.app.post('/community/browse', data=dict(
            searchterm=''
        ), follow_redirects=True)

        assert ('1 - Count to N') in rv.data
        assert ('2 - Sum to N') in rv.data
        assert ('3 - Sum to N^2') in rv.data
        assert ('4 - Subtract 5 from N') in rv.data
        
        # Now try searching for special character '^'
        rv = self.app.post('/community/browse', data=dict(
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
        rv = self.app.post('/submit?challenge_id=1',data=dict(
            editor="printf",
            language = 'C'
            ),follow_redirects=True)

        assert('error') in rv.data
        assert('printf') in rv.data

        rv = self.app.get('/submissions/4', follow_redirects=True)
        assert('Status: Compile Error') in rv.data

        #submit valid code
        rv = self.app.post('/submit?challenge_id=1',data=dict(
            editor="int main(){return 0;}",
            language = 'C'
            ),follow_redirects=True)
        assert('Program output') in rv.data

        rv = self.app.get('/submissions/6', follow_redirects=True)
        assert('Status: Incorrect') in rv.data
        #test another challenge for submission
        rv = self.app.post('/submit?challenge_id=2',data=dict(
            editor="int main(){return 0;}",
            language = 'C'
            ),follow_redirects=True)
        assert('Program output') in rv.data

        rv = self.app.post('/submit?challenge_id=2',data=dict(
            editor="printf",
            language = 'C'
            ),follow_redirects=True)
        assert('error') in rv.data
        assert('printf') in rv.data

        #passing all the tests
        rv = self.app.post('/submit?challenge_id=1',data=dict(
            editor='''#include <stdio.h> 
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

        rv = self.app.post('/submit?challenge_id=1',data=dict(
            editor='''#include <stdio.h> 
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

        rv = self.app.post('/submit?challenge_id=1',data=dict(
            editor='''#include <stdio.h> 
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
        rv = self.app.post('/submit?challenge_id=1',data=dict(
            editor='''import java.util.Scanner;
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
        rv = self.app.post('/submit?challenge_id=1',data=dict(
            editor='''import java.util.Scanner;
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
   
    def test_python_submission(self):
        self.login('admin','default')

        #all tests passed
        rv = self.app.post('/submit?challenge_id=1',data=dict(
            editor='''number = raw_input()
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
        rv = self.app.post('/submit?challenge_id=2',data=dict(
            editor='''#include<iostream>
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
        # Check if we can see our 3 challenges that are pre-populated
        assert('Accepted') in rv.data
        assert('Incorrect') in rv.data
        assert('Compile Error') in rv.data
        assert('Something Else') not in rv.data
        # Check submission languages work
        assert('Python') in rv.data
        assert('C++') in rv.data
        assert('C') in rv.data
        assert('<td>Java</td>') not in rv.data # There's a false positive for Java in a comment relating to minified Javascript

    # Test database imported specific submission is working as intended
    def test_specific_submission(self):
        self.login('dannyeei', 'daniel')
        rv = self.app.get('/submissions/1', follow_redirects=True)
        assert('Accepted') in rv.data
        assert('This is a status info') in rv.data
        assert('I would have like a compile error or something in here') in rv.data
        assert('Blab blah you failed some testcases man') not in rv.data

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

    # Test display playlist page
    def test_no_playlist(self):
        rv = self.app.get('/playlists/0', follow_redirects=True)
        # Check dropdown menu is operational
        assert("Count to N") in rv.data
        assert("Sum to N") in rv.data
        assert("Invert Case") in rv.data
        assert("Number of As") in rv.data
        assert("Dota 2 is a great game") not in rv.data

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

    # Test creating a new playlist
    def test_new_playlist(self):
        self.login('typical', 'typical')
        rv = self.app.get('/new_playlist', follow_redirects=True)
        assert ("Count to N") in rv.data
        assert ("Sum to N") in rv.data
        assert ("Dota 2 is a great game") in rv.data
        assert ("Valve cant program") in rv.data
        
        # Testing empty strings and whitespace names fail
        data = {}
        data['playlist_name'] = ""
        rv = self.app.post('/new_playlist', data=data, follow_redirects=True)
        assert ("Please insert a valid username.") in rv.data

        data['playlist_name'] = "          "
        rv = self.app.post('/new_playlist', data=data, follow_redirects=True)
        assert ("Please insert a valid username.") in rv.data

        data['playlist_name'] = "Stanley Sux"
        data['Count to N'] = "1"
        data['Valve cant program'] = "4"
        rv = self.app.post('/new_playlist', data=data, follow_redirects=True)
        assert ("New playlist <b>Stanley Sux</b> created with ID") in rv.data

        data['playlist_name'] = "Stanley Sux"
        rv = self.app.post('/new_playlist', data=data, follow_redirects=True)
        assert ("<b>Stanley Sux</b> already exists.") in rv.data

        rv = self.app.get('/playlists', follow_redirects=True)
        rv = self.app.post('/playlists',data=dict(
                    selected_name = 'Stanley Sux'
                    ), follow_redirects=True)
        assert ("Count to N: 1") in rv.data
        assert ("Valve cant program: 2") in rv.data
        assert ("Sum to N") not in rv.data
        assert ("Dota 2 is a great game") not in rv.data

    def test_submit_old_playlist(self):
        self.login('dannyeei', 'daniel')
        rv = self.app.get('/new_playlist', follow_redirects=True)
        data = {}
        data['playlist_name'] = "Stanley Sux"
        data['Count to N'] = "1"
        data['Valve cant program'] = "4"
        rv = self.app.post('/new_playlist', data=data, follow_redirects=True)
        rv = self.app.post('/playlists',data=dict(
                    selected_name = 'Stanley Sux'
                    ), follow_redirects=True)
        assert ("Count to N") in rv.data
        assert ("Valve cant program") in rv.data
        data = {}
        data['reorder'] = "Submit Changes"
        data['selected_name'] = "Stanley Sux"
        data['Count to N'] = "1"
        data['Valve cant program'] = "2"
        rv = self.app.post('/playlists', data=data, follow_redirects=True)  
        assert ("Count to N") in rv.data
        assert ("Valve cant program") in rv.data

    def test_delete_playlist(self):
        self.login('dannyeei', 'daniel')
        rv = self.app.get('/playlists', follow_redirects=True)
        assert("<option selected>my playlist first ever") in rv.data
        assert ("Count to N") in rv.data
        assert ("Dota 2 is a great game") in rv.data
        assert ("Valve cant program") not in rv.data
        
        # Testing empty strings and whitespace names fail
        data = {}
        data['delete_list'] = "my playlist first ever"
        rv = self.app.post('/playlists', data=data, follow_redirects=True)
        assert ("my playlist first ever") not in rv.data
        assert ("Count to N") not in rv.data
        assert ("Dota 2 is a great game") in rv.data
        assert ("Valve cant program") in rv.data
        assert("<option selected>my second playlist ever") in rv.data

        data['delete_list'] = "my second playlist ever"
        rv = self.app.post('/playlists', data=data, follow_redirects=True)
        assert ("You have no playlists.") in rv.data


    # Test a challenge shows the correct "add to playlist" buttons in the dropdown
    def test_add_to_playlist(self):
        self.login('dannyeei', 'daniel')
        rv = self.app.get('/new_playlist', follow_redirects=True)
        # Create empty playlist Stanley Sux
        data = {}
        data['playlist_name'] = "Stanley Sux"
        rv = self.app.post('/new_playlist', data=data, follow_redirects=True)
        rv = self.app.post('/playlists',data=dict(
                    selected_name = 'Stanley Sux'
                    ), follow_redirects=True)
        assert ("Count to N") not in rv.data
        assert ("Sum to N") not in rv.data

        # Add Count to N to playlist
        rv = self.app.get('/browse/Count%20to%20N', follow_redirects=True)
        assert("Add to \"my playlist first ever\"") in rv.data
        assert("Add to \"my second playlist ever\"") in rv.data
        assert("Add to \"Stanley Sux\"") in rv.data
        rv = self.app.get('/browse/Count%20to%20N?playlist_name=Stanley+Sux', follow_redirects=True)
        assert("<b>Count to N</b> has been added to <b>Stanley Sux</b>") in rv.data
        # Check that it accounts for already existing challenges
        rv = self.app.get('/browse/Count%20to%20N?playlist_name=Stanley+Sux', follow_redirects=True)
        assert("<b>Count to N</b> already exists in <b>Stanley Sux</b>") in rv.data

        # Add Sum to N to playlist
        rv = self.app.get('/browse/Sum%20to%20N', follow_redirects=True)
        assert("Create a program that prints sum 1..n") in rv.data
        assert("Add to \"my playlist first ever\"") in rv.data
        assert("Add to \"my second playlist ever\"") in rv.data
        assert("Add to \"Stanley Sux\"") in rv.data
        rv = self.app.get('/browse/Sum%20to%20N?playlist_name=Stanley+Sux', follow_redirects=True)
        assert("<b>Sum to N</b> has been added to <b>Stanley Sux</b>") in rv.data

        # Test playlist manager shows added challenges
        rv = self.app.post('/playlists',data=dict(
                    selected_name = 'Stanley Sux'
                    ), follow_redirects=True)
        assert ("Count to N") in rv.data
        assert ("Sum to N") in rv.data


    def test_new_forum(self):
        self.login('typical', 'typical')
        rv = self.app.get('/forums/1', follow_redirects=True)
        assert("This is a forum question") not in rv.data
        rv = self.app.post('/forums-new/1', follow_redirects=True, data=dict(question="This is a forum question", postbody="This bit explains what the forum question is in more detail"))
        assert("This bit explains what the forum question is in more detail") in rv.data
        assert("This is a forum question") in rv.data
        rv = self.app.get('/forums/1', follow_redirects=True)
        assert("This is a forum question") in rv.data

    def test_comment_forum(self):
        self.login('typical', 'typical')
        rv = self.app.get('/forums/1', follow_redirects=True)
        assert("This is a forum question") not in rv.data
        rv = self.app.post('/forums-new/1', follow_redirects=True, data=dict(question="This is a forum question", postbody="This bit explains what the forum question is in more detail"))
        assert("This bit explains what the forum question is in more detail") in rv.data
        assert("This is a forum question") in rv.data
        assert("This is a comment. Commenty commenty comment") not in rv.data
        rv = self.app.post('/forums/1/1', data=dict(comment="This is a comment. Commenty commenty comment"))
        assert("This is a comment. Commenty commenty comment") in rv.data

    # check user stanley has by default challenges 1 6 completed, admin has none.
    def test_completed_challenges(self):
        self.login('stanley', 'default')
        rv = self.app.get('/myprofile')
        assert("No challenges completed.") not in rv.data
        assert("1 6") in rv.data
        rv = self.logout()
        self.login('admin', 'default')
        rv = self.app.get('/myprofile')
        assert("No challenges completed.") in rv.data
        assert("1 3") not in rv.data

    # submit an answer for Q1 and Q6, check profile shows those two problems solved.
    def test_completed_challenges_2(self):
        self.login('admin', 'default')
        rv = self.app.get('/myprofile')
        assert("No challenges completed.") in rv.data
        
        # Submit problem 1
        rv = self.app.post('/submit?challenge_id=1',data=dict(
            editor='''#include <stdio.h> 
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

        # Submit problem2 
        rv = self.app.post('/submit?challenge_id=2',data=dict(
            editor='''#include<iostream>
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

        # Check /myprofile shows 1 2
        rv = self.app.get('/myprofile')
        assert("1 2") in rv.data
        assert("No challenges completed.") not in rv.data

    # Test browse page shows completion status correctly
    def test_completed_challenges_3(self):
        # Admin has no completed challenges, so YES should not be on the browse page
        rv = self.login('admin', 'default')
        rv = self.app.get('/browse')
        assert("YES") not in rv.data

        rv = self.logout()
        rv = self.login('stanley', 'default')
        rv = self.app.get('/browse')
        assert("Yes") in rv.data
        # Also assert it's in twice not just once
        assert(rv.data.count("Yes") == 2)


    # Test adding to a category then displaying filtered challenges


if __name__ == '__main__':
    unittest.main()
