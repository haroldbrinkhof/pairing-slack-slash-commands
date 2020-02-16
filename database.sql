CREATE TABLE pairings(id SERIAL PRIMARY KEY,person_id text NOT NULL, pairs_with text NOT NULL, starting timestamp not null DEFAULT now(), ending timestamp NOT NULL DEFAULT now(), message text NULL);

CREATE TABLE availability(id serial PRIMARY KEY, channel_id text NOT NULL, channel_name text NOT NULL, person_id text NOT NULL, person_name text NOT NULL, still_available BOOL DEFAULT TRUE, offered_on date DEFAULT CURRENT_DATE, optional_message text NULL, UNIQUE(channel_id, person_id, offered_on));
