CREATE TABLE IF NOT EXISTS jokes (
	id integer PRIMARY KEY AUTOINCREMENT,
	api_id varchar,
	value text,
	created_at datetime,
	updated_at datetime
);

CREATE TABLE IF NOT EXISTS categories (
	id integer PRIMARY KEY AUTOINCREMENT,
	name varchar
);

CREATE TABLE IF NOT EXISTS joke_categories (
	id integer PRIMARY KEY AUTOINCREMENT,
	jokes_id integer,
	categories_id integer
);
