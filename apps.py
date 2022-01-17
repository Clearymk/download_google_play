import os

# devices = ["emulator-5556", "emulator-5558"]
devices = ["emulator-5558"]
# for device in devices:
#     res = os.popen("adb -s {} shell pm list packages".format(device)).readlines()
#     with open("base_app_id", "w") as f:
#         for app_id in res:
#             f.write(app_id.strip().replace("package:", "") + "\n")
#     print(res)
#     print(len(res))
base_app_ids = []

with open("base_app_id", "r") as f:
    for line in f.readlines():
        base_app_ids.append(line.strip())

for device in devices:
    res = os.popen("adb -s {} shell pm list packages".format(device)).readlines()
    print(len(res))
    # for app_id in res:
    #     app_id = app_id.strip().replace("package:", "")
    #     if app_id not in base_app_ids:
    #         print(app_id)
    #         os.popen("adb -s {} uninstall {}".format(device, app_id)).readlines()
