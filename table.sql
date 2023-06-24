CREATE TABLE logs (
        id_logs SERIAL PRIMARY KEY,
        ip VARCHAR(15),
        dt DATE,
        query TEXT,
        cond INTEGER,
        byt_send TEXT
    )
