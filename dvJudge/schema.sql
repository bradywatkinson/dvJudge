
drop table if exists users;
create table users (
	id integer primary key autoincrement,
	username text not null,
	email text not null,
	password text not null,
	salt text not null
);

drop table if exists challenges;
create table challenges (
	id integer primary key autoincrement,
	name text not null,
	description text not null,
	input text,
	output text,
	sample_input text,
	sample_output text
);
