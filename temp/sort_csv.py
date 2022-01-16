import csv

data_0 = []
data_1 = []
with open("../apk_pure_info.csv", "r") as f:
    reader = csv.reader(f)
    for row in reader:
        if row[5] == "1":
            data_1.append(row)
        if row[5] == "0":
            data_0.append(row)

with open("../apk_pure_info.csv", "w", newline="") as f:
    writer = csv.writer(f)
    for row in data_0:
        writer.writerow(row)

    for row in data_1:
        writer.writerow(row)
