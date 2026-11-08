$ErrorActionPreference = 'Stop'
. "$PSScriptRoot/start-demo.ps1"
function Assert($Condition, $Message) { if (-not $Condition) { throw $Message } }
function Assert-Throws($Action, $Pattern) {
    $message = $null
    try { & $Action } catch { $message = $_.Exception.Message }
    Assert ($message -and $message -match $Pattern) "Expected error matching $Pattern; got $message"
}
$scratch = Join-Path ([IO.Path]::GetTempPath()) ([guid]::NewGuid().ToString())
New-Item -ItemType Directory -Path $scratch | Out-Null
try {
    $path = Join-Path $scratch 'checkpoint.json'
    Assert-Throws { Get-DemoCheckpoint $path } 'Missing'
    '{"model":"tinker://test/model","expires_at":"2000-01-01T00:00:00Z"}' | Set-Content $path
    Assert-Throws { Get-DemoCheckpoint $path } 'expired'
    '{"model":"https://wrong","expires_at":"2099-01-01T00:00:00Z"}' | Set-Content $path
    Assert-Throws { Get-DemoCheckpoint $path } 'Invalid'
    '{"model":"tinker://test/model","expires_at":"2099-01-01T00:00:00Z"}' | Set-Content $path
    Assert ((Get-DemoCheckpoint $path).model -eq 'tinker://test/model') 'Valid checkpoint rejected'

    function Get-NetTCPConnection { [pscustomobject]@{ LocalPort = 8081; OwningProcess = 4242 } }
    function Stop-Process { throw 'Must never stop processes' }
    Assert-Throws { Assert-DemoPortFree } 'PID: 4242'
    function Get-NetTCPConnection { @() }
    Assert-DemoPortFree

    $originalPython = ${function:Test-DemoPython}
    $oldOverride = $env:DOBBY_PYTHON
    try {
        $script:seen = @()
        $env:DOBBY_PYTHON = 'explicit-python'
        function Test-DemoPython($Path) { $script:seen += $Path; return $Path -eq 'explicit-python' }
        Assert ((Get-DemoPython) -eq 'explicit-python') 'Override not preferred'
        function Test-DemoPython($Path) { $script:seen += $Path; return $Path -eq 'python' }
        Assert ((Get-DemoPython) -eq 'python') 'Broken candidates did not fall through'
        function Test-DemoPython($Path) { return $Path -like '*micromamba*python.exe' }
        Assert ((Get-DemoPython) -like '*micromamba*python.exe') 'Host fallback not found'
    } finally {
        $env:DOBBY_PYTHON = $oldOverride
        Set-Item Function:Test-DemoPython $originalPython
    }

    $tokens = @(1..32 | ForEach-Object { New-DemoToken })
    Assert (@($tokens | Select-Object -Unique).Count -eq 32) 'Tokens repeated'
    Assert (@($tokens | Where-Object { $_ -notmatch '^[a-f0-9]{64}$' }).Count -eq 0) 'Token format wrong'
    # CheckOnly uses mocked prerequisites and cannot reach a cloud command.
    function Get-DemoCheckpoint { [pscustomobject]@{model='tinker://test/model'; expires_at='2099-01-01T00:00:00Z'} }
    function Get-DemoPython { 'fake-python' }
    function Get-DemoGcloud { 'forbidden-cloud-command' }
    function forbidden-cloud-command { throw 'Cloud command called during check-only' }
    $CheckOnly = $true
    Start-Demo
    $CheckOnly = $false
    $script:DemoRoot = $scratch
    New-Item -ItemType Directory -Path (Join-Path $scratch '.venv'), (Join-Path $scratch 'backend') | Out-Null
    $requirements = Join-Path $scratch 'backend/requirements.txt'
    [IO.File]::WriteAllText($requirements, 'abc', (New-Object Text.UTF8Encoding $false))
    Assert ((Get-DemoRequirementsHash $requirements) -eq 'BA7816BF8F01CFEA414140DE5DAE2223B00361A396177A9CB410FF61F20015AD') 'Real SHA256 hashing failed known-content check'
    Set-Content $requirements 'fake==1'
    Set-Content (Join-Path $scratch '.venv/dobby-demo-ready') (Get-DemoRequirementsHash $requirements)
    function Test-DemoPython { $true }
    function Get-DemoGcloud { Join-Path $scratch 'sdk/bin/fake-cloud' }
    $fakeCloud = Get-DemoGcloud
    $fakeVenv = Join-Path $scratch '.venv/Scripts/python.exe'
    $script:expectedSdkPython = 'inherited-sdk-python'
    $script:pipCalls = 0
    Set-Item "Function:$fakeCloud" {
        Assert ($env:CLOUDSDK_PYTHON -eq $script:expectedSdkPython) 'SDK Python selection incorrect'
        Assert ($ErrorActionPreference -eq 'Continue') 'Native warning handling not localized'
        $global:LASTEXITCODE = 0
        'fake-key-for-mocked-test'
    }
    Set-Item "Function:$fakeVenv" {
        if ($args[1] -eq 'pip') { $script:pipCalls++; $global:LASTEXITCODE = 0; return }
        Assert ($args[1] -eq 'uvicorn') 'Unexpected dependency reinstall'
        Assert ($env:TINKER_BASE_URL -eq 'https://tinker.thinkingmachines.dev/services/tinker-prod/oai/api/v1') 'Inherited provider URL reached server'
        Assert ((Get-Location).Path -eq (Join-Path $scratch 'backend')) 'Server working directory incorrect'
        $global:LASTEXITCODE = 0
    }
    $oldBase = $env:TINKER_BASE_URL
    $oldSdkPython = $env:CLOUDSDK_PYTHON
    $oldLocation = (Get-Location).Path
    try {
        $env:TINKER_BASE_URL = 'https://untrusted.invalid'
        $env:CLOUDSDK_PYTHON = 'inherited-sdk-python'
        Start-Demo
        Assert ($env:TINKER_BASE_URL -eq 'https://untrusted.invalid') 'Provider URL not restored'
        Assert ($env:CLOUDSDK_PYTHON -eq 'inherited-sdk-python') 'SDK Python not restored'
        Assert ((Get-Location).Path -eq $oldLocation) 'Working directory not restored'
        Assert ($ErrorActionPreference -eq 'Stop') 'Error handling not restored'
        Assert ($script:pipCalls -eq 0) 'Unchanged requirements reinstalled'
        Set-Content $requirements 'fake==2'
        $env:CLOUDSDK_PYTHON = $null
        $script:expectedSdkPython = 'fake-python'
        Start-Demo
        Assert ($script:pipCalls -eq 1) 'Changed requirements did not reinstall exactly once'
        $bundled = Join-Path $scratch 'sdk/platform/bundledpython'
        New-Item -ItemType Directory -Path $bundled -Force | Out-Null
        Set-Content (Join-Path $bundled 'python.exe') 'fake'
        $script:expectedSdkPython = $null
        Start-Demo
        Assert ($script:pipCalls -eq 1) 'Matching dependency hash reinstalled'
        Assert (-not $env:CLOUDSDK_PYTHON) 'Empty SDK Python not restored'
        Set-Content (Join-Path $scratch '.venv/dobby-demo-ready') '' -NoNewline
        Start-Demo
        Assert ($script:pipCalls -eq 2) 'Empty dependency marker did not reinstall safely'
    } finally {
        $env:TINKER_BASE_URL = $oldBase
        $env:CLOUDSDK_PYTHON = $oldSdkPython
    }
    Write-Host 'PASS: checkpoint, port safety, Python selection, tokens, offline CheckOnly, fixed provider URL/restoration, SDK Python, dependency hash, and server working directory.'
} finally {
    $tempRoot = [IO.Path]::GetFullPath([IO.Path]::GetTempPath()).TrimEnd('\') + '\'
    $cleanupTarget = [IO.Path]::GetFullPath($scratch)
    if (-not $cleanupTarget.StartsWith($tempRoot, [StringComparison]::OrdinalIgnoreCase) -or $cleanupTarget -eq $tempRoot.TrimEnd('\')) {
        throw 'Refusing scratch cleanup outside the intended temporary directory.'
    }
    Remove-Item -LiteralPath $scratch -Recurse -Force
}
