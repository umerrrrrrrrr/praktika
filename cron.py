import json; import re as r; import psycopg2
with open('cfg.json') as cfg_file:
    cfg = json.load(cfg_file)

def db_update():
    hand.execute(
        """
        DELETE FROM logs;
        """
    )
    with open(cfg["log_file_path"], 'r') as log_file:
        for line in log_file:
            match = sampler.match(line)
            if match:
                ip = match.group(1); log_name = match.group(2); usr = match.group(3); date = match.group(4); query = match.group(5); cond = int(match.group(6)); byt_send = match.group(7)
                hand.execute(
                    """
                    INSERT INTO logs (ip, log_name, usr, dt, query, cond, byt_send)
                    VALUES (%s, %s, %s, %s, %s, %s, %s)
                    """,
                    (ip, log_name, usr, date, query, cond, byt_send)
                )
    con.commit()

db_cfg = cfg["database"]
con = psycopg2.connect(
    host = db_cfg["host"],
    port = db_cfg["port"],
    database = db_cfg["database"],
    user = db_cfg["user"],
    password = db_cfg["password"]
)

sampler = r.compile(r'^(\S+) (\S+) (\S+) \[(.*?)\] "(.*?)" (\d+) (\d+|-)$'); hand = con.cursor()