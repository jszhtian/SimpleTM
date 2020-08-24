
BEGIN TRANSACTION;
PRAGMA foreign_keys = ON;
CREATE TABLE User
(
    id VARCHAR(255) NOT NULL,
    salt text NOT NULL,
    PRIMARY KEY (id)
);
CREATE UNIQUE INDEX user_index 
    ON USER (id);
CREATE TABLE Game
(
    id text NOT NULL,
    title text,
    PRIMARY KEY (id)
);
CREATE UNIQUE INDEX game_index 
    ON Game (id);
CREATE TABLE Translate
(
    game_id text NOT NULL,
    raw_word text NOT NULL,
    trans_word text,
    PRIMARY KEY (game_id, raw_word),
    FOREIGN KEY (game_id) REFERENCES Game(id)
        ON DELETE CASCADE
        ON UPDATE CASCADE
);
CREATE INDEX translate_index 
    ON Translate (game_id);
CREATE TABLE Permission
(
    user_id int NOT NULL,
    game_id text NOT NULL, 
    permission int NOT NULL, --(none=0, read=1, write=2, admin=3)
    FOREIGN KEY (user_id) REFERENCES User(id)
        ON DELETE CASCADE 
        ON UPDATE CASCADE,
    FOREIGN KEY (game_id) REFERENCES Game(id)
        ON DELETE CASCADE 
        ON UPDATE CASCADE
);
CREATE UNIQUE INDEX permission_index 
    ON Permission (user_id, game_id);

INSERT INTO User VALUES ('jsc', 'bf91a58a6c67908f16a00bde8ac81215de71c937611f858f8ff1a320b8c7a89d');
INSERT INTO Game VALUES ('imoyaba', '妹のおかげでモテすげてヤバイ。');
INSERT INTO Game VALUES ('kamiyaba', '神頼みしすぎて俺の未来がヤバい。');
INSERT INTO Game VALUES ('sennrennbannka', '千恋万花');
INSERT INTO Game VALUES ('hoshikoi-tinkle', '星恋tinkle');
INSERT INTO Translate VALUES ('imoyaba', 'test_raw', 'test_translation');
INSERT INTO Translate VALUES ('imoyaba', 'test_raw2', 'test_translation2');
INSERT INTO Translate VALUES ('kamiyaba', 'kami1', 'kami1-t');
INSERT INTO Permission VALUES ('jsc', 'imoyaba', 3);
INSERT INTO Permission VALUES ('jsc', 'kamiyaba', 2);
INSERT INTO Permission VALUES ('jsc', 'sennrennbannka', 2);
INSERT INTO Permission VALUES ('jsc', 'hoshikoi-tinkle', 1);

COMMIT;
