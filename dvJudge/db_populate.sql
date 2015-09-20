
-- #A single integer — the (comparatic) something of something
-- #The first line contains integer n (? ≤ n ≤ ?) — amount X

-- Challenges
insert into challenges (name,description,input,output,sample_tests,input_desc,output_desc)
	values ('Count to N','Create a program that prints "1..n"',"5","1 2 3 4 5","Input: 10 \n Output: 1 2 3 4 5 6 7 8 9 10","A single integer — the (comparatic) something of something","A single line containing the sequence of integers from 1 to n, i.e. 1 2 3 ... n-1 n");

insert into challenges (name,description,input,output,sample_tests,input_desc,output_desc)
	values ('Sum to N','Create a program that prints sum 1..n',"4","10","Input: 10 \n Output: 55","A single integer — the (comparatic) something of something","A single integer — the sum of the integers from 1..n");

-- Accounts
insert into users (username, email, password)
	values ('dannyeei', 'danielslater811@hotmail.com', 'daniel');

insert into users (username, email, password)
	values ('typical', 'typical@hotmail.com', 'typical');

insert into users (username, email, password)
	values ('admin', 'admin@hotmail.com', 'default');



-- insert into challenges (name,description,input,output,sample_tests)
-- 	values ('Sum to N^2','Create a program that prints sum 1^2..n^2',"4","30",null);
