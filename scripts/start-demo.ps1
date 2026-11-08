param([switch]$CheckOnly)

$ErrorActionPreference = 'Stop'
$script:DemoRoot = Split-Path $PSScriptRoot -Parent

function Get-DemoCheckpoint {
    param([string]$Path)
    if (-not (Test-Path -LiteralPath $Path -PathType Leaf)) {
        throw 'Missing private/tinker-model.json. Complete the controlled Tinker setup first.'
    }
    try {
        $checkpoint = Get-Content -LiteralPath $Path -Raw | ConvertFrom-Json
        $expiry = [DateTimeOffset]::MinValue
        if ($checkpoint.model -isnot [string] -or $checkpoint.model -notmatch '^tinker://\S+$' -or
            $checkpoint.expires_at -isnot [string] -or
            $checkpoint.expires_at -notmatch '^\d{4}-\d{2}-\d{2}T.*(?:Z|[+-]\d{2}:\d{2})$' -or
            -not [DateTimeOffset]::TryParse($checkpoint.expires_at, [ref]$expiry)) {
            throw 'invalid'
        }
    } catch { throw 'Invalid private/tinker-model.json; expected a Tinker model and ISO expires_at with timezone.' }
    if ($expiry -le [DateTimeOffset]::UtcNow) { throw 'Tinker checkpoint expired. Repeat the controlled Tinker setup.' }
    return $checkpoint
}

function Assert-DemoPortFree {
    $listeners = @(Get-NetTCPConnection -State Listen -ErrorAction Stop | Where-Object LocalPort -eq 8081)
    if ($listeners.Count) {
        $owners = ($listeners | Select-Object -ExpandProperty OwningProcess -Unique) -join ', '
        throw "Port 8081 is occupied (PID: $owners). No process was stopped."
    }
}

function Test-DemoPython {
    param([string]$Path)
    if (-not $Path) { return $false }
    try {
        & $Path -c 'import sys; sys.exit(0 if sys.version_info >= (3, 10) else 1)' *> $null
        return $LASTEXITCODE -eq 0
    } catch { return $false }
}

function Get-DemoPython {
    $candidates = @($env:DOBBY_PYTHON, (Join-Path $script:DemoRoot '.venv/Scripts/python.exe'),
        'python', (Join-Path $env:USERPROFILE 'micromamba/envs/ds/python.exe'))
    foreach ($candidate in $candidates) {
        if (Test-DemoPython $candidate) { return $candidate }
    }
    throw 'No working Python 3.10+ found. Install Python or set DOBBY_PYTHON to python.exe.'
}

function Get-DemoGcloud {
    $standard = Join-Path $env:LOCALAPPDATA 'Google/Cloud SDK/google-cloud-sdk/bin/gcloud.cmd'
    if (Test-Path -LiteralPath $standard -PathType Leaf) { return $standard }
    $command = Get-Command gcloud.cmd -ErrorAction SilentlyContinue
    if ($command) { return $command.Source }
    throw 'Google Cloud CLI is missing. Install it and sign in before starting the demo.'
}

function New-DemoToken {
    $bytes = New-Object byte[] 32
    $rng = [Security.Cryptography.RandomNumberGenerator]::Create()
    try { $rng.GetBytes($bytes) } finally { $rng.Dispose() }
    return ([BitConverter]::ToString($bytes)).Replace('-', '').ToLowerInvariant()
}

function Get-DemoRequirementsHash {
    param([string]$Path)
    $sha = [Security.Cryptography.SHA256]::Create()
    try {
        $stream = [IO.File]::OpenRead($Path)
        try { return ([BitConverter]::ToString($sha.ComputeHash($stream))).Replace('-', '') }
        finally { $stream.Dispose() }
    } finally { $sha.Dispose() }
}

function Start-Demo {
    $checkpoint = Get-DemoCheckpoint (Join-Path $script:DemoRoot 'private/tinker-model.json')
    Assert-DemoPortFree
    $python = Get-DemoPython
    $gcloud = Get-DemoGcloud
    if ($CheckOnly) {
        Write-Host "Prerequisites OK. Python: $python; port: 8081; checkpoint expires: $($checkpoint.expires_at). No cloud or model calls made."
        return
    }

    $venv = Join-Path $script:DemoRoot '.venv/Scripts/python.exe'
    $ready = Join-Path $script:DemoRoot '.venv/dobby-demo-ready'
    $requirements = Join-Path $script:DemoRoot 'backend/requirements.txt'
    $requirementsHash = Get-DemoRequirementsHash $requirements
    if (-not (Test-DemoPython $venv)) {
        & $python -m venv (Join-Path $script:DemoRoot '.venv')
        if ($LASTEXITCODE -ne 0) { throw 'Could not create local Python environment.' }
        Remove-Item -LiteralPath $ready -ErrorAction SilentlyContinue
    }
    if (-not (Test-Path -LiteralPath $ready) -or "$((Get-Content -LiteralPath $ready -Raw))".Trim() -ne $requirementsHash) {
        & $venv -m pip install -r $requirements
        if ($LASTEXITCODE -ne 0) { throw 'Backend dependency installation failed.' }
        Set-Content -LiteralPath $ready -Value $requirementsHash
    }
    $names = @('CLOUDSDK_PYTHON', 'TINKER_API_KEY', 'TINKER_MODEL', 'TINKER_BASE_URL', 'MODEL_PROVIDER', 'DEMO_API_TOKEN')
    $previous = @{}
    foreach ($name in $names) { $previous[$name] = [Environment]::GetEnvironmentVariable($name, 'Process') }
    try {
        $bundledPython = Join-Path (Split-Path (Split-Path $gcloud -Parent) -Parent) 'platform/bundledpython/python.exe'
        if (-not $env:CLOUDSDK_PYTHON -and -not (Test-Path -LiteralPath $bundledPython -PathType Leaf)) {
            $env:CLOUDSDK_PYTHON = $python
        }
        $savedErrorAction = $ErrorActionPreference
        try {
            $ErrorActionPreference = 'Continue'
            $key = & $gcloud secrets versions access latest --secret=phish-tinker-key --project=lateral-nomad-514001-c7 2>$null
            $secretExitCode = $LASTEXITCODE
        } catch { throw 'Could not read the Tinker key. Check Google Cloud sign-in and Secret Manager access.' }
        finally { $ErrorActionPreference = $savedErrorAction }
        if ($secretExitCode -ne 0 -or -not $key -or @($key).Count -ne 1) {
            throw 'Could not read the Tinker key. Check Google Cloud sign-in and Secret Manager access.'
        }
        $env:TINKER_API_KEY = "$key".Trim()
        if (-not $env:TINKER_API_KEY) { throw 'Secret Manager returned an empty Tinker key.' }
        $key = $null
        $env:TINKER_MODEL = $checkpoint.model
        $env:TINKER_BASE_URL = 'https://tinker.thinkingmachines.dev/services/tinker-prod/oai/api/v1'
        $env:MODEL_PROVIDER = 'tinker'
        $env:DEMO_API_TOKEN = New-DemoToken
        Assert-DemoPortFree
        Write-Host 'Direct local demo: http://127.0.0.1:8081. Keep this window open; Ctrl+C stops it.'
        Write-Host "Checkpoint expires: $($checkpoint.expires_at). Startup does not create a sampler or run inference."
        Write-Host 'Choose direct local in the extension, paste this temporary token into its password field, and explicitly enable Tinker:'
        Write-Host $env:DEMO_API_TOKEN
        Push-Location (Join-Path $script:DemoRoot 'backend')
        try {
            & $venv -m uvicorn --app-dir (Join-Path $script:DemoRoot 'backend') main:app --host 127.0.0.1 --port 8081 --no-access-log
            if ($LASTEXITCODE -ne 0) { throw 'Demo server stopped with an error.' }
        } finally { Pop-Location }
    } finally {
        $key = $null
        foreach ($name in $names) { [Environment]::SetEnvironmentVariable($name, $previous[$name], 'Process') }
    }
}

if ($MyInvocation.InvocationName -ne '.') {
    try { Start-Demo } catch { Write-Host "Demo could not start: $($_.Exception.Message)" -ForegroundColor Red; exit 1 }
}
