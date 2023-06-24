import tkinter as tk; import subprocess; import json; import re as r; import psycopg2; from psycopg2.extras import RealDictCursor; from datetime import datetime
with open('cfg.json') as cfg_file:
    cfg = json.load(cfg_file)

def get_logs(option):
    class DateTimeEncoder(json.JSONEncoder):
        def default(self, obj):
            if isinstance(obj, datetime):
                return obj.isoformat()
            return super().default(obj)

    def get_log(sd = None, ed = None, groupip = False):
        hand = con.cursor(cursor_factory = RealDictCursor)
        query_sql = """
            SELECT ip, log_name, usr, dt, query, cond, byt_send
            FROM logs
        """
        args = []; circs = []
        if sd:
            circs.append("dt >= %s"); args.append(sd)
        if ed:
            circs.append("dt <= %s"); args.append(ed)
        if circs:
            query_sql += "WHERE " + " AND ".join(circs)
        if groupip:
            query_sql += " GROUP BY ip"
        hand.execute(query_sql, args); output = hand.fetchall(); hand.close()
        return output

    sd = sd_entry.get(); ed = ed_entry.get(); groupip = groupip_var.get(); log = get_log(sd = sd, ed = ed, groupip = groupip)
    
    if option:
        termout.delete(1.0, tk.END)
        for i, log in enumerate(log):
            termout.insert(tk.END, f"Лог #{i + 1}\n"); termout.insert(tk.END, f"ip: {log['ip']}\n"); termout.insert(tk.END, f"log_name: {log['log_name']}\n"); termout.insert(tk.END, f"usr: {log['usr']}\n"); termout.insert(tk.END, f"dt: {log['dt'].strftime('%Y-%m-%d %H:%M:%S')}\n"); termout.insert(tk.END, f"query: {log['query']}\n"); termout.insert(tk.END, f"cond: {log['cond']}\n"); termout.insert(tk.END, f"byt_send: {log['byt_send']}\n")
    else:
        json_log = json.dumps(log, cls = DateTimeEncoder)
        with open('logs.json', 'w') as logs_file:
            logs_file.write(json_log)

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
agregator = tk.Tk(); agregator.title("agregator")

def displaytermout():
    with open('logs.json', 'r') as logs_file:
        termout.insert(tk.END, logs_file.read())

def id_btn_click(id_btn):
    if id_btn == 1:
        db_update()
    elif id_btn == 2:
        get_logs(True)
    elif id_btn == 3:
        get_logs(False)

btn1 = tk.Button(agregator, text = "Update DB", command = lambda: id_btn_click(1)); btn1.pack(); btn2 = tk.Button(agregator, text = "Show logs", command = lambda: id_btn_click(2)); btn2.pack(); btn3 = tk.Button(agregator, text = "Upload on JSON file", command = lambda: id_btn_click(3)); btn3.pack()
termout = tk.Text(agregator, height = 50, width = 100); termout.pack()
sd_label = tk.Label(agregator, text = "Start date:"); sd_label.pack(); sd_entry = tk.Entry(agregator); sd_entry.pack()
ed_label = tk.Label(agregator, text = "End date:"); ed_label.pack(); ed_entry = tk.Entry(agregator); ed_entry.pack()
groupip_var = tk.IntVar(); groupip_label = tk.Label(agregator, text = "Group by ip:"); groupip_label.pack(); groupip_1 = tk.Radiobutton(agregator, text = "Yes", variable = groupip_var, value = 1); groupip_1.pack(); groupip_0 = tk.Radiobutton(agregator, text = "No", variable = groupip_var, value = 0); groupip_0.pack()
displaytermout(); agregator.mainloop()