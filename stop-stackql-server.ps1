# stop-stackql-server.ps1
# Stop the stackql server started by start-stackql-server.ps1.
# Match the 'srv' invocation specifically (via the process command line) so we
# don't kill unrelated stackql.exe processes or anything that merely has
# "stackql" in its path.

$procs = Get-CimInstance Win32_Process -Filter "Name = 'stackql.exe'" -ErrorAction SilentlyContinue |
    Where-Object { $_.CommandLine -match 'srv' }

if (-not $procs) {
    Write-Host "stackql server is not running."
} else {
    foreach ($p in $procs) {
        Write-Host "stopping stackql server (PID: $($p.ProcessId))..."
        Stop-Process -Id $p.ProcessId -Force -ErrorAction SilentlyContinue
    }
    Write-Host "stackql server stopped."
}
