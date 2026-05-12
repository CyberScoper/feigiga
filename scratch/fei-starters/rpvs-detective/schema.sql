-- RPVS Detective SQLite schema
PRAGMA journal_mode = WAL;
PRAGMA foreign_keys = ON;

CREATE TABLE IF NOT EXISTS partners (
    id            INTEGER PRIMARY KEY,
    cislo_vlozky  INTEGER NOT NULL
);

CREATE TABLE IF NOT EXISTS companies (
    id              INTEGER PRIMARY KEY,
    partner_id      INTEGER NOT NULL REFERENCES partners(id) ON DELETE CASCADE,
    role            TEXT    NOT NULL CHECK (role IN ('pvs','oo')),
    ico             TEXT,
    obchodne_meno   TEXT,
    forma_osoby     TEXT,
    platnost_od     TEXT,
    platnost_do     TEXT
);
CREATE INDEX IF NOT EXISTS idx_companies_partner ON companies(partner_id);
CREATE INDEX IF NOT EXISTS idx_companies_ico     ON companies(ico);

CREATE TABLE IF NOT EXISTS persons (
    id                  INTEGER PRIMARY KEY,
    partner_id          INTEGER NOT NULL REFERENCES partners(id) ON DELETE CASCADE,
    role                TEXT    NOT NULL CHECK (role IN ('kuv','vf')),
    meno                TEXT,
    priezvisko          TEXT,
    datum_narodenia     TEXT,
    je_verejny_cinitel  INTEGER DEFAULT 0,
    titul_pred          TEXT,
    titul_za            TEXT,
    platnost_od         TEXT,
    platnost_do         TEXT
);
CREATE INDEX IF NOT EXISTS idx_persons_partner    ON persons(partner_id);
CREATE INDEX IF NOT EXISTS idx_persons_priezvisko ON persons(priezvisko);

-- FTS5 для быстрого человеческого поиска
CREATE VIRTUAL TABLE IF NOT EXISTS persons_fts USING fts5(
    meno, priezvisko, content='persons', content_rowid='id', tokenize='unicode61'
);
CREATE VIRTUAL TABLE IF NOT EXISTS companies_fts USING fts5(
    obchodne_meno, ico, content='companies', content_rowid='id', tokenize='unicode61'
);

-- Триггеры синхронизации FTS с основной таблицей
CREATE TRIGGER IF NOT EXISTS persons_ai AFTER INSERT ON persons BEGIN
    INSERT INTO persons_fts(rowid, meno, priezvisko) VALUES (new.id, new.meno, new.priezvisko);
END;
CREATE TRIGGER IF NOT EXISTS persons_ad AFTER DELETE ON persons BEGIN
    INSERT INTO persons_fts(persons_fts, rowid, meno, priezvisko) VALUES ('delete', old.id, old.meno, old.priezvisko);
END;
CREATE TRIGGER IF NOT EXISTS companies_ai AFTER INSERT ON companies BEGIN
    INSERT INTO companies_fts(rowid, obchodne_meno, ico) VALUES (new.id, new.obchodne_meno, new.ico);
END;
CREATE TRIGGER IF NOT EXISTS companies_ad AFTER DELETE ON companies BEGIN
    INSERT INTO companies_fts(companies_fts, rowid, obchodne_meno, ico) VALUES ('delete', old.id, old.obchodne_meno, old.ico);
END;

-- Метаданные ингеста
CREATE TABLE IF NOT EXISTS ingest_meta (
    key         TEXT PRIMARY KEY,
    value       TEXT
);
