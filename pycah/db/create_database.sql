DROP TABLE IF EXISTS users;
DROP TABLE IF EXISTS expansions;
DROP TABLE IF EXISTS black_cards;
DROP TABLE IF EXISTS white_cards;
DROP TABLE IF EXISTS games;
DROP TABLE IF EXISTS game_users;
DROP TABLE IF EXISTS game_expansions;
DROP TABLE IF EXISTS game_moves;

CREATE TABLE users (
	uid BIGSERIAL PRIMARY KEY NOT NULL,
	username CHARACTER VARYING(255) NOT NULL UNIQUE,
	password CHARACTER VARYING(255) NOT NULL,
	salt CHARACTER VARYING(255) NOT NULL
);

CREATE TABLE expansions (
	eid SMALLSERIAL PRIMARY KEY NOT NULL,
	name CHARACTER VARYING(255) NOT NULL UNIQUE,
	description TEXT
);

CREATE TABLE white_cards (
	eid SMALLINT NOT NULL,
	cid SMALLSERIAL,
	trump BOOLEAN NOT NULL,        -- Might need other booleans?
	value TEXT,
	PRIMARY KEY (eid, cid),
	FOREIGN KEY (eid) REFERENCES expansions(eid)
);

CREATE TABLE black_cards (
	eid SMALLINT NOT NULL,
	cid SMALLSERIAL,
	type SMALLINT NOT NULL,
	value TEXT,
	PRIMARY KEY (eid, cid),
	FOREIGN KEY (eid) REFERENCES expansions(eid)
);

CREATE TABLE games (
	gid BIGSERIAL PRIMARY KEY,
	win_points SMALLINT NOT NULL
);

CREATE TABLE game_users (
	gid BIGINT NOT NULL,
	uid BIGINT NOT NULL,
	points SMALLINT NOT NULL,
	FOREIGN KEY (gid) REFERENCES games(gid),
	FOREIGN KEY (uid) REFERENCES users(uid),
	UNIQUE (gid, uid)
);

CREATE TABLE game_expansions (
	gid BIGINT NOT NULL,
	eid SMALLINT NOT NULL,
	FOREIGN KEY (gid) REFERENCES games(gid),
	FOREIGN KEY (eid) REFERENCES expansions(eid)
);

--CREATE TABLE game_moves (
--	gid BIGINT NOT NULL,
--	uid BIGINT NOT NULL,
--);
