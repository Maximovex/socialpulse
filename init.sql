CREATE EXTENSION IF NOT EXISTS vector;

CREATE TABLE IF NOT EXISTS stories (
    id                INTEGER PRIMARY KEY,
    title             TEXT,
    score             INTEGER,
    author            VARCHAR(50),
    url               TEXT,
    time              TIMESTAMP,
    kids_count        INTEGER,
    type              VARCHAR(20),
    controversy_score FLOAT,
    sentiment         FLOAT,
    sentiment_label   VARCHAR(10),
    roberta_label     VARCHAR(10),
    roberta_score     FLOAT,
    embedding         VECTOR(768)
);
