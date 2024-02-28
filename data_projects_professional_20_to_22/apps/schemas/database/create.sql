CREATE TABLE partners (
	id SERIAL PRIMARY KEY,
	company TEXT,
	country TEXT
);

CREATE TABLE projects (
	id SERIAL PRIMARY KEY,
	partner_id INT REFERENCES partners(id),
	title TEXT,
	description TEXT
);

CREATE TABLE languages (
	id INT PRIMARY KEY,
	code VARCHAR(4),
	name TEXT,
	UNIQUE(id)
);

CREATE TABLE tags (
	id SERIAL PRIMARY KEY,
	name TEXT
);

CREATE TABLE corpus (
	id SERIAL PRIMARY KEY,
	lang_id INT REFERENCES languages(id),
	text TEXT 
);
CREATE INDEX idx_corpus_lang_id ON corpus(lang_id);

CREATE TABLE cnt_mono_corpus (
	id SERIAL PRIMARY KEY,
	lang_id1 INT REFERENCES languages(id),
	tag_id INT,
	cnt INT,
	UNIQUE(lang_id1, tag_id)
);
CREATE INDEX idx_cnt_mono_corpus_lang_id ON cnt_mono_corpus(lang_id1);

CREATE VIEW cnt_mono_corpus_per_tag AS
SELECT (SELECT code FROM languages WHERE id = lang_id1) AS code1,
	(SELECT name FROM tags WHERE id = tag_id) AS tag,
	cnt AS count
FROM cnt_mono_corpus
ORDER BY code1, tag_id

CREATE TABLE cnt_2pairs_corpus (
	id SERIAL PRIMARY KEY,
	lang_id1 INT REFERENCES languages(id),
	lang_id2 INT REFERENCES languages(id),
	tag_id INT,
	cnt INT,
	UNIQUE(lang_id1, lang_id2, tag_id)
);
CREATE INDEX idx_cnt_2pairs_corpus_lang_id ON cnt_2pairs_corpus(lang_id1, lang_id2);

CREATE VIEW cnt_2pairs_corpus_per_tag AS
SELECT (SELECT code FROM languages WHERE id = lang_id1) AS code1,
	(SELECT code FROM languages WHERE id = lang_id2) AS code2,
	(SELECT name FROM tags WHERE id = tag_id) AS tag,
	cnt AS count
FROM cnt_2pairs_corpus
ORDER BY lang_id1, lang_id2, tag_id

CREATE TABLE cnt_3pairs_corpus (
	id SERIAL PRIMARY KEY,
	lang_id1 INT REFERENCES languages(id),
	lang_id2 INT REFERENCES languages(id),
	lang_id3 INT REFERENCES languages(id),
	tag_id INT,
	cnt INT,
	UNIQUE(lang_id1, lang_id2, lang_id3, tag_id)
);
CREATE INDEX idx_cnt_3pairs_corpus_lang_id ON cnt_3pairs_corpus(lang_id1, lang_id2, lang_id3);

CREATE VIEW corpus_by_group AS
SELECT group_id, corpus_id,
	(SELECT code FROM languages WHERE id = lang_id) AS code,
	(SELECT text FROM corpus WHERE id = corpus_id) AS corpus
FROM parallel_corpus
ORDER BY code;

CREATE TABLE duplicated_corpus (
	id SERIAL PRIMARY KEY,
	group_id INT,
	lang_id INT REFERENCES languages(id),
	corpus_id1 INT REFERENCES corpus(id),
	corpus_id2 INT REFERENCES corpus(id)
);
CREATE INDEX idx_duplicated_corpus_group_id ON duplicated_corpus(group_id);

CREATE TABLE parallel_corpus (
	id SERIAL PRIMARY KEY,
	group_id INT,
	lang_id INT REFERENCES languages(id),
	corpus_id INT REFERENCES corpus(id)
);
CREATE INDEX idx_parallel_corpus_group_id ON parallel_corpus(group_id);
CREATE INDEX idx_parallel_corpus_lang_id ON parallel_corpus(lang_id);
CREATE INDEX idx_parallel_corpus_corpus_id ON parallel_corpus(corpus_id);

CREATE TABLE corpus_tags_map (
	id SERIAL PRIMARY KEY,
	group_id INT,
	tag_id INT REFERENCES tags(id),
	priority INT,
	UNIQUE(group_id, priority)
);
CREATE INDEX idx_corpus_tags_map_group_id ON corpus_tags_map(group_id);

CREATE TABLE group_tags_map (
	id SERIAL PRIMARY KEY,
	group_id INT,
	tag_id INT REFERENCES tags(id),
	priority INT,
	score REAL,
	UNIQUE(group_id, priority)
);
CREATE INDEX idx_group_tags_map_group_id ON group_tags_map(group_id);

CREATE TABLE project_corpus_map (
	id SERIAL PRIMARY KEY,
	project_id INT REFERENCES projects(id),
	lang_id INT REFERENCES languages(id),
	corpus_id INT REFERENCES corpus(id)
);
CREATE INDEX idx_project_corpus_map_project_lang_corpus_id ON project_corpus_map(project_id, lang_id, corpus_id);
CREATE INDEX idx_project_corpus_map_project_id ON project_corpus_map(project_id);
CREATE INDEX idx_project_corpus_map_lang_id ON project_corpus_map(lang_id);
CREATE INDEX idx_project_corpus_map_corpus_id ON project_corpus_map(corpus_id);

CREATE VIEW parallel_corpus_h AS
SELECT id,
	group_id,
	(SELECT code FROM languages WHERE id = lang_id),
	(SELECT text FROM corpus WHERE id = corpus_id)
FROM parallel_corpus;

CREATE VIEW corpus_info AS
SELECT g.id,
	group_id,
	(SELECT code FROM languages WHERE id = g.lang_id) AS lang_code,
	(SELECT text FROM corpus WHERE id = corpus_id) AS text,
	(SELECT title FROM projects WHERE id IN (SELECT project_id FROM project_corpus_map WHERE lang_id = g.lang_id AND corpus_id = g.corpus_id ORDER BY id DESC LIMIT 1)) AS project,
	(SELECT name FROM tags WHERE id = (SELECT tag_id FROM corpus_tags_map WHERE group_id = g.group_id ORDER BY id DESC LIMIT 1)) AS tag
FROM parallel_corpus g, corpus c
WHERE g.corpus_id = c.id
ORDER BY lang_code;

CREATE FUNCTION select_group(a integer)
RETURNS TABLE(id int, group_id int, lang_code text, corpus_id int, text text, project text, tag text) AS $$
	SELECT
		id, 
		group_id,
		(SELECT code FROM languages WHERE id = lang_id) AS lang_code,
		corpus_id,
		(SELECT text FROM corpus WHERE id = corpus_id) AS text,
		(SELECT title FROM projects WHERE id IN (SELECT project_id FROM project_corpus_map WHERE lang_id = p.lang_id AND corpus_id = p.corpus_id ORDER BY id DESC LIMIT 1)) AS project,
		(SELECT name FROM tags WHERE id = (SELECT tag_id FROM corpus_tags_map WHERE group_id = p.group_id ORDER BY id DESC LIMIT 1)) AS tag 
	FROM parallel_corpus p
	WHERE group_id = $1
	ORDER BY lang_code
$$ LANGUAGE SQL;

CREATE FUNCTION select_corpus(a integer)
RETURNS TABLE(id int, group_id int, lang_code text, corpus_id int, text text, project text, tag text) AS $$
	SELECT
		id,
		group_id,
		(SELECT code FROM languages WHERE id = lang_id) AS lang_code,
		corpus_id,
		(SELECT text FROM corpus WHERE id = corpus_id) AS text,
		(SELECT title FROM projects WHERE id IN (SELECT project_id FROM project_corpus_map WHERE lang_id = p.lang_id AND corpus_id = p.corpus_id ORDER BY id DESC LIMIT 1)) AS project,
		(SELECT name FROM tags WHERE id = (SELECT tag_id FROM corpus_tags_map WHERE group_id = p.group_id ORDER BY id DESC LIMIT 1)) AS tag
	FROM parallel_corpus p
	WHERE group_id IN (
		SELECT group_id
		FROM parallel_corpus
		WHERE corpus_id = $1)
	ORDER BY lang_code;
$$ LANGUAGE SQL;

CREATE VIEW corpus_per_project AS
SELECT A.project_id, A.group_id,
	A.lang_id AS lang_id1, B.lang_id AS lang_id2,
	A.corpus_id AS corpus_id1, B.corpus_id AS corpus_id2,
	(SELECT text FROM corpus WHERE id = A.corpus_id) AS corpus1,
	(SELECT text FROM corpus WHERE id = B.corpus_id) AS corpus2
FROM
	(SELECT m.project_id, c.group_id, c.lang_id, c.corpus_id
	FROM parallel_corpus c, project_corpus_map m
	WHERE c.corpus_id = m.corpus_id) A,
	(SELECT m.project_id, c.group_id, c.lang_id, c.corpus_id
	FROM parallel_corpus c, project_corpus_map m
	WHERE c.corpus_id = m.corpus_id) B
WHERE A.group_id = B.group_id
	AND A.lang_id < B.lang_id
ORDER BY group_id, A.lang_id, B.lang_id, A.corpus_id, B.corpus_id;

CREATE VIEW delivery AS
SELECT (SELECT title FROM projects WHERE id = project_id),
	lang_id1, lang_id2,
	COUNT(*) AS count
FROM corpus_per_project
GROUP BY project_id, lang_id1, lang_id2
ORDER BY project_id, lang_id1, lang_id2;

CREATE VIEW multiple_corpus AS
SELECT A.group_id,
	A.lang_id AS lang_id1, A.corpus_id AS source_corpus_id,
	B.lang_id AS lang_id2, B.corpus_id1 AS current_corpus_id, B.corpus_id2 AS new_corpus_id,
	(SELECT text FROM corpus WHERE id = A.corpus_id) AS source_text,
	(SELECT text FROM corpus WHERE id = B.corpus_id1) AS current_text,
	(SELECT text FROM corpus WHERE id = B.corpus_id2) AS new_text
FROM (SELECT id, group_id, lang_id, corpus_id
	FROM parallel_corpus
	WHERE group_id IN (SELECT group_id
		FROM duplicated_corpus)
	ORDER BY group_id) A,
	duplicated_corpus B
WHERE A.group_id = B.group_id
	AND A.lang_id <> B.lang_id
ORDER BY B.id;

CREATE TABLE user_meta (
	id INT UNIQUE,
	name TEXT,
	country INT REFERENCES country(country_id),
	gender CHAR(1),
	age_group INT
);

CREATE TABLE voice_corpus (
	id SERIAL PRIMARY KEY,
	lang_id INT REFERENCES languages(id),
	text TEXT,
	voice_url TEXT,
	user_id INT REFERENCES user_meta(id),
	partner_id INT REFERENCES partners(id)
);
CREATE INDEX idx_voice_corpus_lang_id ON voice_corpus(lang_id);
