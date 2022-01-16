import os
import time

import mysql.connector
from mysql.connector.errors import IntegrityError
from download_app import DownloadApp

con = mysql.connector.connect(user='root', password='sqlClear1998', database='xapk')
cur = con.cursor()
cur.execute("SELECT * FROM xapk.app")

class Listener:
    def __init__(self):
        self.row = 0
        self.max_row = 142353

    def update_row(self, row):
        self.row = row

    def start_listen(self):
        while len(cur.fetchall()) >= 1 and self.row < self.max_row:
            print("当前处理" + str(self.row))
            cur.execute("SELECT app_id FROM xapk.app")
            res = cur.fetchall()

            for app_id in res:
                res = os.popen("adb shell pm list packages").readlines()
                flag = False
                if "package:" + app_id[0] + "\n" in res:
                    flag = True

                if flag:
                    res = os.popen("adb shell pm path " + app_id[0]).readlines()
                    if len(res) == 1:
                        print(res)
                        cur.execute("DELETE FROM xapk.app WHERE app_id=%s", (app_id[0]), )
                        con.commit()
                        print("one apk find uninstall it")
                        print(os.popen("adb uninstall " + app_id[0]).readlines())
                    elif len(res) > 1:
                        try:
                            cur.execute("INSERT INTO xapk.xapk(app_id) VALUES (%s)", (app_id[0],))
                            con.commit()
                        except IntegrityError:
                            print()

                        print(os.popen("mkdir /Volumes/Data/apk_pure/play_xapk/" + app_id[0]).readlines())
                        print("muti apk find extract it")
                        for path in res:
                            path = path.split('package:')[1].strip()
                            print(
                                os.popen(
                                    "adb pull " + path + " /Volumes/Data/apk_pure/play_xapk/" + app_id[0]).readlines())

                            cur.execute("DELETE FROM xapk.app WHERE app_id=%s", (app_id[0],))
                            con.commit()
                            print(os.popen("adb uninstall " + app_id[0]).readlines())
                    print("--------")
                print("+++++++++")
            time.sleep(10)
            cur.execute("SELECT app_id FROM xapk.app")
