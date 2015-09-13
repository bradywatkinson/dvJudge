drop table if exists entries;
create table entries (
  id integer primary key autoincrement,
  title text not null,
  text text not null
);

drop table if exists users;
create table users (
	id integer primary key autoincrement,
	username text not null,
	password text not null
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
