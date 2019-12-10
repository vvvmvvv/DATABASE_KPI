CREATE TABLE clubs
 (
  club_id            SERIAL PRIMARY KEY,
  name               VARCHAR(80) NOT NULL UNIQUE,
  creation_date      DATE        NOT NULL,
  number_of_trophies INTEGER     NOT NULL
);


CREATE TABLE positions
 (
  position_id SERIAL PRIMARY KEY,
  name        VARCHAR(80) NOT NULL
);

INSERT INTO positions (name) VALUES ('Goalkeeper'), ('Defender'), ('Midfielder'), ('Forward');

CREATE TABLE players
(
  player_id     SERIAL PRIMARY KEY,
  first_name    text        NOT NULL,
  last_name     VARCHAR(80) NOT NULL,
  date_of_birth DATE        NOT NULL,
  is_injured  boolean     NOT NULL,
  height        INTEGER     NOT NULL,
  club_id       INTEGER,
  position_id   INTEGER     NOT NULL,
  FOREIGN KEY (club_id)
  REFERENCES clubs (club_id)
  ON DELETE SET NULL,
  FOREIGN KEY (position_id)
  REFERENCES positions (position_id)
);


CREATE TABLE tournaments
 (
  tournament_id SERIAL PRIMARY KEY,
  name VARCHAR(80) NOT NULL,
  description text NOT NULL,
  tsv tsvector NOT NULL
);

CREATE INDEX text_search_idx ON tournaments USING GIN (tsv);

CREATE TRIGGER tsvectorupdate BEFORE INSERT OR UPDATE
ON tournaments
FOR EACH ROW EXECUTE PROCEDURE
tsvector_update_trigger(tsv, 'pg_catalog.english', description);

CREATE TABLE clubs_tournaments
 (
  club_id       INTEGER NOT NULL,
  tournament_id INTEGER NOT NULL,
  PRIMARY KEY (club_id, tournament_id),
  FOREIGN KEY (club_id)
  REFERENCES clubs (club_id)
  ON UPDATE CASCADE ON DELETE CASCADE,
  FOREIGN KEY (tournament_id)
  REFERENCES tournaments (tournament_id)
  ON UPDATE CASCADE ON DELETE CASCADE
)
