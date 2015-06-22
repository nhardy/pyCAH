DROP TABLE IF EXISTS users CASCADE;
DROP TABLE IF EXISTS expansions CASCADE;
DROP TABLE IF EXISTS black_cards CASCADE;
DROP TABLE IF EXISTS white_cards CASCADE;
DROP TABLE IF EXISTS games CASCADE;
DROP TABLE IF EXISTS game_users CASCADE;
DROP TABLE IF EXISTS game_expansions CASCADE;
DROP TABLE IF EXISTS game_czar CASCADE;
DROP TABLE IF EXISTS game_moves CASCADE;
DROP TABLE IF EXISTS game_cards CASCADE;


CREATE TABLE users (
	uid BIGSERIAL PRIMARY KEY,
	username CHARACTER VARYING(255) NOT NULL UNIQUE,
	password CHARACTER VARYING(255) NOT NULL,
	salt CHARACTER VARYING(255) NOT NULL
);

CREATE TABLE expansions (
	eid SMALLSERIAL PRIMARY KEY,
	name CHARACTER VARYING(255) NOT NULL UNIQUE,
	description TEXT
);

CREATE TABLE white_cards (
	eid SMALLINT NOT NULL,
	cid SMALLINT NOT NULL DEFAULT 0,
	trump BOOLEAN NOT NULL,        -- Might need other booleans?
	value TEXT,
	PRIMARY KEY (eid, cid),
	FOREIGN KEY (eid) REFERENCES expansions(eid)
);

CREATE OR REPLACE FUNCTION wc_cid_auto()
	RETURNS trigger AS $$
BEGIN
	SELECT COALESCE(MAX(cid) + 1, 1)
	INTO NEW.cid
	FROM white_cards
	WHERE eid = NEW.eid;

	RETURN NEW;
END;
$$ LANGUAGE plpgsql STRICT;

CREATE TRIGGER wc_cid_auto
	BEFORE INSERT ON white_cards
	FOR EACH ROW WHEN (NEW.cid = 0)
	EXECUTE PROCEDURE wc_cid_auto();

CREATE TABLE black_cards (
	eid SMALLINT NOT NULL,
	cid SMALLINT NOT NULL DEFAULT 0,
	type SMALLINT NOT NULL,
	value TEXT,
	PRIMARY KEY (eid, cid),
	FOREIGN KEY (eid) REFERENCES expansions(eid)
);

CREATE OR REPLACE FUNCTION bc_cid_auto()
	RETURNS trigger AS $$
BEGIN
	SELECT COALESCE(MAX(cid) + 1, 1)
	INTO NEW.cid
	FROM black_cards
	WHERE eid = NEW.eid;

	RETURN NEW;
END;
$$ LANGUAGE plpgsql STRICT;

CREATE TRIGGER bc_cid_auto
	BEFORE INSERT ON black_cards
	FOR EACH ROW WHEN (NEW.cid = 0)
	EXECUTE PROCEDURE bc_cid_auto();

CREATE TABLE games (
	gid BIGSERIAL PRIMARY KEY,
	uid BIGINT NOT NULL,
	win_points SMALLINT NOT NULL,
	FOREIGN KEY (uid) REFERENCES users(uid)
);

CREATE TABLE game_users (
	gid BIGINT NOT NULL,
	uid BIGINT NOT NULL,
	PRIMARY KEY (gid, uid),
	FOREIGN KEY (gid) REFERENCES games(gid),
	FOREIGN KEY (uid) REFERENCES users(uid)
);

CREATE TABLE game_expansions (
	gid BIGINT NOT NULL,
	eid SMALLINT NOT NULL,
	PRIMARY KEY (gid, eid),
	FOREIGN KEY (gid) REFERENCES games(gid),
	FOREIGN KEY (eid) REFERENCES expansions(eid)
);

CREATE TABLE game_czar (
	gid BIGINT NOT NULL,
	round SMALLINT NOT NULL DEFAULT 0,
	czar_id BIGINT NOT NULL,
	eid SMALLINT NOT NULL,
	cid SMALLINT NOT NULL,
	winner_id BIGINT,
	PRIMARY KEY (gid, round),
	FOREIGN KEY (gid) REFERENCES games(gid),
	FOREIGN KEY (gid, czar_id) REFERENCES game_users(gid, uid),
	FOREIGN KEY (eid, cid) REFERENCES black_cards(eid, cid),
	FOREIGN KEY (gid, winner_id) REFERENCES game_users(gid, uid)
);

CREATE OR REPLACE FUNCTION game_round_auto()
	RETURNS trigger AS $$
BEGIN
	SELECT COALESCE(MAX(round) + 1, 1)
	INTO NEW.round
	FROM game_czar
	WHERE gid = NEW.gid;

	RETURN NEW;
END;
$$ LANGUAGE plpgsql STRICT;

CREATE TRIGGER game_round_auto
	BEFORE INSERT ON game_czar
	FOR EACH ROW WHEN (NEW.round = 0)
	EXECUTE PROCEDURE game_round_auto();

CREATE TABLE game_moves (
	gid BIGINT NOT NULL,
	round SMALLINT NOT NULL,
	uid BIGINT NOT NULL,
	eid SMALLINT NOT NULL,
	cid SMALLINT NOT NULL,
	time TIMESTAMP NOT NULL, -- For ordering of white card placements
	PRIMARY KEY (gid, round, uid, time),
	FOREIGN KEY (gid) REFERENCES games(gid),
	FOREIGN KEY (gid, round) REFERENCES game_czar(gid, round),
	FOREIGN KEY (gid, uid) REFERENCES game_users(gid, uid),
	FOREIGN KEY (eid, cid) REFERENCES white_cards(eid, cid)
);

CREATE TABLE game_cards (
	gid BIGINT NOT NULL,
	uid BIGINT NOT NULL,
	eid SMALLINT NOT NULL,
	cid SMALLINT NOT NULL,
	used BOOLEAN NOT NULL,
	PRIMARY KEY (gid, uid, eid, cid),
	FOREIGN KEY (gid) REFERENCES games(gid),
	FOREIGN KEY (gid, uid) REFERENCES game_users(gid, uid),
	FOREIGN KEY (eid, cid) REFERENCES white_cards(eid, cid)
);
