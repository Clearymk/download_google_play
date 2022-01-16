import mysql.connector
import csv

conn = mysql.connector.connect(user='root', password='sqlClear1998', database='xapk')
cur = conn.cursor()
cur.execute("SELECT * FROM xapk.play_download WHERE status = 0 AND id > 100000")

with open("extract_task.csv", "w") as f:
    writer = csv.writer(f)
    for data in cur.fetchall():
        writer.writerow(data)