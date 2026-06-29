#Requires -Version 5
<#
run_tests.ps1 - Provision a venv, ensure stackql.exe, then run the full
PyStackQL test suite (local + server) on Windows and print a summary.

Steps:
  1. Create/activate a Python venv and install dependencies
  2. Ensure stackql.exe exists in the current directory (download if not)
  3. Start the stackql server
  4. Run the local tests   (run_tests.py)
  5. Run the server tests  (run_server_tests.py)
  6. Stop the stackql server
  7. Print a PASS/FAIL summary with totals

This is the PowerShell/Windows counterpart of run_tests.sh.
Run it with:  .\run_tests.ps1
#>

$ProgressPreference = 'SilentlyContinue'

# Run from the script's own directory so relative paths resolve correctly.
Set-Location -Path $PSScriptRoot

# Configuration
$VenvName         = '.venv'
$VenvPython       = Join-Path $VenvName 'Scripts\python.exe'
$RequirementsFile = 'requirements.txt'
$LocalRunner      = 'run_tests.py'
$ServerRunner     = 'run_server_tests.py'
$StartServer      = '.\start-stackql-server.ps1'
$StopServer       = '.\stop-stackql-server.ps1'
$Installer        = 'https://get-stackql.io/install'

function Write-Section($msg) { Write-Host $msg -ForegroundColor Blue }
function Write-Ok($msg)      { Write-Host $msg -ForegroundColor Green }
function Write-Warn($msg)    { Write-Host $msg -ForegroundColor Yellow }
function Write-Err($msg)     { Write-Host $msg -ForegroundColor Red }
function StatusText($code)   { if ($code -eq 0) { 'PASS' } else { 'FAIL' } }
function StatusColor($code)  { if ($code -eq 0) { 'Green' } else { 'Red' } }

# Extract the pytest summary line (e.g. "43 passed, 1 skipped") from a log file
function Get-PytestSummary($logPath) {
    $match = Get-Content $logPath -ErrorAction SilentlyContinue |
        Select-String -Pattern 'passed|failed|error|no tests ran' |
        Select-Object -Last 1
    if ($null -eq $match) { return '' }
    return (($match.Line) -replace '=', '' -replace 'in [\d.]+s', '').Trim()
}

# Banner
Write-Section "======================================="
Write-Section "  PyStackQL Test Runner                "
Write-Section "======================================="
Write-Host ""

# --- 1. Python venv setup -------------------------------------------------

if (-not (Get-Command python -ErrorAction SilentlyContinue)) {
    Write-Err "Error: Python is not installed or not on PATH."
    exit 1
}

Write-Warn "Using Python:"
python --version
Write-Host ""

if (-not (Test-Path $VenvPython)) {
    Write-Warn "Creating virtual environment in $VenvName..."
    python -m venv $VenvName
    if (-not (Test-Path $VenvPython)) {
        Write-Err "Error: Failed to create virtual environment."
        exit 1
    }
    Write-Ok "Virtual environment created successfully."
} else {
    Write-Warn "Using existing virtual environment in $VenvName"
}

Write-Warn "Upgrading pip, setuptools, and wheel..."
& $VenvPython -m pip install --upgrade pip setuptools wheel | Out-Null

if (Test-Path $RequirementsFile) {
    Write-Warn "Installing dependencies from $RequirementsFile..."
    & $VenvPython -m pip install -r $RequirementsFile | Out-Null
    if ($LASTEXITCODE -ne 0) { Write-Err "Warning: Some dependencies may have failed to install." }
    else { Write-Ok "Dependencies installed successfully." }
} else {
    Write-Err "Warning: $RequirementsFile not found, skipping dependency install."
}

if ((Test-Path 'pyproject.toml') -or (Test-Path 'setup.py')) {
    Write-Warn "Installing PyStackQL in development mode..."
    & $VenvPython -m pip install -e . | Out-Null
    if ($LASTEXITCODE -ne 0) { Write-Err "Warning: Failed to install package in development mode." }
    else { Write-Ok "Package installed in development mode." }
}
Write-Host ""

# --- 2. Ensure a stackql.exe in the current directory ---------------------

if (Test-Path '.\stackql.exe') {
    Write-Ok "Found stackql binary: $((Get-Item '.\stackql.exe').FullName)"
} else {
    Write-Warn "No stackql.exe in $($PWD.Path), downloading..."
    Invoke-RestMethod $Installer | Invoke-Expression
    if (-not (Test-Path '.\stackql.exe')) {
        Write-Err "Error: stackql.exe was not installed to $($PWD.Path)."
        exit 1
    }
    Write-Ok "stackql.exe installed: $((Get-Item '.\stackql.exe').FullName)"
}
Write-Host ""

# --- 3-6. Start server, run both suites, always stop server ---------------

$localCode = 1; $localSummary = ''
$serverCode = 1; $serverSummary = ''

Write-Section "Starting stackql server..."
& $StartServer
Write-Host ""

try {
    # Local tests
    Write-Section "======================================="
    Write-Section "  Running local tests ($LocalRunner)"
    Write-Section "======================================="
    $localLog = New-TemporaryFile
    & $VenvPython $LocalRunner | Tee-Object -FilePath $localLog.FullName
    $localCode = $LASTEXITCODE
    $localSummary = Get-PytestSummary $localLog.FullName
    Remove-Item $localLog -Force -ErrorAction SilentlyContinue
    Write-Host ""

    # Server tests
    Write-Section "======================================="
    Write-Section "  Running server tests ($ServerRunner)"
    Write-Section "======================================="
    $serverLog = New-TemporaryFile
    & $VenvPython $ServerRunner | Tee-Object -FilePath $serverLog.FullName
    $serverCode = $LASTEXITCODE
    $serverSummary = Get-PytestSummary $serverLog.FullName
    Remove-Item $serverLog -Force -ErrorAction SilentlyContinue
    Write-Host ""
}
finally {
    Write-Section "Stopping stackql server..."
    & $StopServer
    Write-Host ""
}

# --- 7. Summary -----------------------------------------------------------

if (($localCode -eq 0) -and ($serverCode -eq 0)) { $overallCode = 0 } else { $overallCode = 1 }

$localText  = if ($localSummary)  { $localSummary }  else { 'no results' }
$serverText = if ($serverSummary) { $serverSummary } else { 'no results' }

Write-Section "======================================="
Write-Section "  Test Summary                         "
Write-Section "======================================="
Write-Host ("  {0,-14} " -f 'Local tests:') -NoNewline
Write-Host (StatusText $localCode) -ForegroundColor (StatusColor $localCode) -NoNewline
Write-Host ("  ({0})" -f $localText)
Write-Host ("  {0,-14} " -f 'Server tests:') -NoNewline
Write-Host (StatusText $serverCode) -ForegroundColor (StatusColor $serverCode) -NoNewline
Write-Host ("  ({0})" -f $serverText)
Write-Section "---------------------------------------"
Write-Host ("  {0,-14} " -f 'Overall:') -NoNewline
Write-Host (StatusText $overallCode) -ForegroundColor (StatusColor $overallCode)
Write-Section "======================================="

exit $overallCode
