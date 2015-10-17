-- Challenges
insert into challenges (name,description,input,output,sample_tests,input_desc,output_desc,com_flag)
	values ('Count to N','Create a program that prints "1..n"',"5","1 2 3 4 5","Input: 10; Output: 1 2 3 4 5 6 7 8 9 10","A single integer — the (comparatic) something of something","A single line containing the sequence of integers from 1 to n, i.e. 1 2 3 ... n-1 n",2);

insert into challenges (name,description,input,output,sample_tests,input_desc,output_desc,com_flag)
	values ('Sum to N','Create a program that prints sum 1..n',"4","10","Input: 10; Output: 55","A single integer — the (comparatic) something of something","A single integer — the sum of the integers from 1..n",2);

insert into challenges (name,description,input,output,sample_tests,input_desc,output_desc,com_flag)
	values ('Dota 2 is a great game','This is a description',"4","10","Input: 10; Output: 55","A single integer — the (comparatic) something of something","A single integer — the sum of the integers from 1..n",1);

insert into challenges (name,description,input,output,sample_tests,input_desc,output_desc,com_flag)
	values ('Valve cant program','This is a different description',"4","10","Input: 10; Output: 55","A single integer — the (comparatic) something of something","A single integer — the sum of the integers from 1..n",1);

insert into challenges (name,description,input,output,sample_tests,input_desc,output_desc,com_flag)
	values ('Invert Case','Given an input string, print the string with all the letters with their cases swapped.',"AbCd1234.","aBcD1234.","Input: AbC123; Output: aBc123","Any string of characters","Same input string with letter cases swapped", 2);

insert into challenges (name,description,input,output,sample_tests,input_desc,output_desc,com_flag)
	values ('Number of As','Given an input string, print the number of upper and lowercase As that occur.',"AAAbcdaaa","6","Input: abACad123; Output: 3","Any string of characters","A single integer", 2);

-- Accounts
insert into users (username, email, password, salt)
	values ('dannyeei', 'danielslater811@hotmail.com', 'd9bdde89547d18f0d6bd72d9a17133ae2cb023357357f51c5d226cbf2d02a056e89102bed4c29e0f2827a952027c9e0a3c2b3545735f0a1c643427d81fc75281', 'thisissamplesalt');

insert into users (username, email, password, salt)
	values ('typical', 'typical@hotmail.com', 'dcaa9d20adff97448541892dd0f13536e3379e2503b03b67411a69d902237d02b17dc74a9f955f831532d449104004f8151b52f09ddf8c2b18e1d78dc720ade1', 'saltandpepper');

insert into users (username, email, password, salt)
	values ('admin', 'admin@hotmail.com', '0b491227c0328e4c87c03fe4749b0b3a78d6da7094f5ef249b99caa759c6f1b1b6c952abb73e9448c5468fb7635f2d90a2f83b14e466c95b19b100fb9aec3c19', 'yumyumsaltinmytum');

insert into users (username, email, password, salt, solved_challenges)
	values ('stanley', 'stanleyhon348@gmail.com', '0b491227c0328e4c87c03fe4749b0b3a78d6da7094f5ef249b99caa759c6f1b1b6c952abb73e9448c5468fb7635f2d90a2f83b14e466c95b19b100fb9aec3c19', 'yumyumsaltinmytum', '1|6');

    -- Submissions
insert into submissions (user_id, challenge_id, status, status_info, language)
    values ('1', 1, 'Accepted', 'This is a status info\nI would have like a compile error or something in here', 'Python');

insert into submissions (user_id, challenge_id, status, status_info, language)
    values ('1', 2, 'Incorrect', 'Blab blah you failed some testcases man', 'C++');

insert into submissions (user_id, challenge_id, status, status_info, language)
    values ('1', 1, 'Compile Error', 'Do you even C?', 'C');

insert into submissions (user_id, challenge_id, status, status_info, language)
    values ('2', 1, 'Compile Error', 'Do you even C?', 'C');

-- Playlists
insert into playlists (id, name, owner_id, challenges)
    values (0, "Public Challenges", 3, "1|2|5|6");

insert into playlists (id, name, owner_id, challenges)
    values (1, "my playlist first ever", 1, "1|3");

insert into playlists (id, name, owner_id, challenges)
    values (2, "my second playlist ever", 1, "3|4");

insert into playlists (id, name, owner_id, challenges)
    values (3, "different playlist", 2, "1|2|3|4");


