drop table if exists entries;
create table entries (
	id integer primary key autoincrement,
	item_content text not null,
	is_done integer not null
);
