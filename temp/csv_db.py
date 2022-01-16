import csv
import mysql.connector

con = mysql.connector.connect(user='root', password='sqlClear1998', database='xapk')
cur = con.cursor()

with open("../apk_pure_info.csv", "r") as f:
    reader = csv.reader(f)
    for row in reader:
        if row[5] == '0':
            print(row)
            cur.execute("INSERT INTO xapk.play_download(app_id) VALUES (%s)", (row[0],))

con.commit()