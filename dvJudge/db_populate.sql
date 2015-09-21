
-- #A single integer — the (comparatic) something of something
-- #The first line contains integer n (? ≤ n ≤ ?) — amount X

-- Challenges
insert into challenges (name,description,input,output,sample_tests,input_desc,output_desc)
	values ('Count to N','Create a program that prints "1..n"',"5","1 2 3 4 5","Input: 10 \n Output: 1 2 3 4 5 6 7 8 9 10","A single integer — the (comparatic) something of something","A single line containing the sequence of integers from 1 to n, i.e. 1 2 3 ... n-1 n");

insert into challenges (name,description,input,output,sample_tests,input_desc,output_desc)
	values ('Sum to N','Create a program that prints sum 1..n',"4","10","Input: 10 \n Output: 55","A single integer — the (comparatic) something of something","A single integer — the sum of the integers from 1..n");

-- Accounts
insert into users (username, email, password, salt)
	values ('dannyeei', 'danielslater811@hotmail.com', 'd9bdde89547d18f0d6bd72d9a17133ae2cb023357357f51c5d226cbf2d02a056e89102bed4c29e0f2827a952027c9e0a3c2b3545735f0a1c643427d81fc75281', 'thisissamplesalt');

insert into users (username, email, password, salt)
	values ('typical', 'typical@hotmail.com', 'dcaa9d20adff97448541892dd0f13536e3379e2503b03b67411a69d902237d02b17dc74a9f955f831532d449104004f8151b52f09ddf8c2b18e1d78dc720ade1', 'saltandpepper');

insert into users (username, email, password, salt)
	values ('admin', 'admin@hotmail.com', '0b491227c0328e4c87c03fe4749b0b3a78d6da7094f5ef249b99caa759c6f1b1b6c952abb73e9448c5468fb7635f2d90a2f83b14e466c95b19b100fb9aec3c19', 'yumyumsaltinmytum');

