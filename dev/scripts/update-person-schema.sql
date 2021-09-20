BEGIN TRANSACTION;
CREATE TABLE IF NOT EXISTS "person_new" ("id" INTEGER NOT NULL PRIMARY
KEY, "uname" VARCHAR(255) NOT NULL, "role" VARCHAR(255) NOT NULL, "display_name" VARCHAR(255) NOT NULL, "updated" INTEGER NOT NULL);
INSERT INTO person_new SELECT id, uname, role, display_name, updated FROM person;
DROP TABLE person;
ALTER TABLE person_new RENAME TO person;
COMMIT;
