# start-stackql-server.ps1
# Start the stackql server (port 5466) if it is not already running.
# Matches the 'srv' invocation specifically (via the process command line) so a
# repo path containing the word "stackql" cannot cause false detections.

$Address = "127.0.0.1"
$Port = 5466

$running = Get-CimInstance Win32_Process -Filter "Name = 'stackql.exe'" -ErrorAction SilentlyContinue |
    Where-Object { $_.CommandLine -match 'srv' }

if ($running) {
    Write-Host "server is already running"
} else {
    Write-Host "starting stackql server on ${Address}:${Port}..."
    # Bind to loopback only: the tests connect on 127.0.0.1, and binding to
    # loopback avoids the Windows Firewall prompt (loopback is not filtered) and
    # does not expose the server to the network.
    Start-Process -FilePath ".\stackql.exe" `
                  -ArgumentList "-v", "--pgsrv.address=$Address", "--pgsrv.port=$Port", "srv" `
                  -RedirectStandardOutput "stackql-server.log" `
                  -RedirectStandardError "stackql-server.err.log" `
                  -WindowStyle Hidden
    Start-Sleep -Seconds 5
}
