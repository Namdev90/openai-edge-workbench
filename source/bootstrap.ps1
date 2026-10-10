# OpenAI Edge Workbench bootstrap. Windows PowerShell 5.1+, current user.
# No machine-wide execution-policy changes or remote-script evaluation.
[CmdletBinding()]
param([string]$Root = (Join-Path $env:LOCALAPPDATA 'OpenAI-Edge-Workbench'),[switch]$NoLaunch)
$ErrorActionPreference = 'Stop'
$ProgressPreference = 'SilentlyContinue'
[Net.ServicePointManager]::SecurityProtocol = [Net.SecurityProtocolType]::Tls12
[Console]::OutputEncoding = [System.Text.UTF8Encoding]::new($false)
$env:PYTHONUTF8 = '1'
$env:PYTHONIOENCODING = 'utf-8'
New-Item -ItemType Directory -Path $Root -Force | Out-Null
$Diagnostic = Join-Path $Root 'Bootstrap-Diagnostic.txt'
function Status([string]$Text) {
    $line = (Get-Date -Format 'yyyy-MM-dd HH:mm:ss') + '  ' + $Text
    Write-Host $line
    Add-Content -LiteralPath $Diagnostic -Value $line -Encoding UTF8
}
function Refresh-SearchPath {
    $env:Path = [Environment]::GetEnvironmentVariable('Path','Machine') + ';' + [Environment]::GetEnvironmentVariable('Path','User')
}
function Test-Python([string]$Command, [string[]]$Prefix) {
    if ([string]::IsNullOrWhiteSpace($Command)) { return $null }
    try {
        $old = $ErrorActionPreference
        $ErrorActionPreference = 'Continue'
        $output = & $Command @Prefix -c "import sys; print(sys.executable) if sys.version_info >= (3,11) else sys.exit(2)" 2>$null
        $code = $LASTEXITCODE
        $ErrorActionPreference = $old
        if ($code -eq 0) {
            $candidate = @($output | Where-Object { $_ -and (Test-Path -LiteralPath ([string]$_) -PathType Leaf) }) | Select-Object -Last 1
            if ($candidate) { return [string]$candidate }
        }
    } catch { $ErrorActionPreference = 'Stop' }
    return $null
}
function Locate-Uv {
    $cmd = Get-Command uv.exe -ErrorAction SilentlyContinue
    if ($cmd) { return $cmd.Source }
    foreach ($p in @((Join-Path $env:USERPROFILE '.local\bin\uv.exe'), (Join-Path $env:LOCALAPPDATA 'Microsoft\WinGet\Links\uv.exe'))) {
        if (Test-Path -LiteralPath $p -PathType Leaf) { return $p }
    }
    return $null
}
try {
    Status 'Starting the local graphical installer. A browser dashboard will open after bootstrap.'
    $nativeArch = $env:PROCESSOR_ARCHITEW6432
    if (-not $nativeArch) { $nativeArch = $env:PROCESSOR_ARCHITECTURE }
    if ($nativeArch -notin @('AMD64','ARM64')) { throw '64-bit Windows x64 or ARM64 is required.' }
    $python = $null
    $py = Get-Command py.exe -ErrorAction SilentlyContinue
    if ($py) { $python = Test-Python $py.Source @('-3') }
    if (-not $python) {
        foreach ($c in @(Get-Command python.exe -All -ErrorAction SilentlyContinue)) {
            if ($c.Source -match '\\Microsoft\\WindowsApps\\') { continue } # Avoid opening Store execution aliases.
            $python = Test-Python $c.Source @()
            if ($python) { break }
        }
    }
    if ($NoLaunch -and -not $python) { throw 'Verification requires an existing Python 3.11+; no installer was run in NoLaunch mode.' }
    if (-not $python) {
        $uv = Locate-Uv
        if (-not $uv) {
            $winget = Get-Command winget.exe -ErrorAction SilentlyContinue
            if (-not $winget) {
                throw 'WinGet and Python 3.11+ were not found. Install or update Microsoft App Installer from Microsoft Store, then rerun this file. No other tools were changed.'
            }
            Status 'Installing the uv bootstrap manager from the exact WinGet package astral-sh.uv.'
            & $winget.Source install --id astral-sh.uv --exact --source winget --accept-source-agreements --accept-package-agreements --disable-interactivity --silent
            $uvInstallCode = $LASTEXITCODE
            Refresh-SearchPath
            $uv = Locate-Uv
            if (-not $uv) { throw "uv could not be located after installation (exit $uvInstallCode)." }
        }
        $env:UV_NO_CONFIG = '1'
        $env:UV_PYTHON_INSTALL_DIR = Join-Path $Root 'runtimes\uv-python'
        Status 'Discovering the newest normal CPython build in the uv catalog, including alpha/beta releases.'
        $raw = & $uv python list --all-versions --output-format json
        if ($LASTEXITCODE -ne 0) { throw 'uv could not list Python builds.' }
        $catalog = ($raw -join "`n") | ConvertFrom-Json
        $cpu = if ($nativeArch -eq 'ARM64') { 'aarch64' } else { 'x86_64' }
        $choices = @()
        foreach ($item in $catalog) {
            if ($item.key -notlike "cpython-*-windows-$cpu-*" -or $item.key.Contains('+')) { continue }
            $v = [string]$item.version
            if ($v -notmatch '^(\d+)\.(\d+)\.(\d+)(?:(a|b|rc)(\d+))?$') { continue }
            $rank = switch ($Matches[4]) { 'a' {0} 'b' {1} 'rc' {2} default {3} }
            $choices += [pscustomobject]@{Key=[string]$item.key; Version=$v; Major=[int]$Matches[1]; Minor=[int]$Matches[2]; Patch=[int]$Matches[3]; Stage=$rank; Number=[int]$Matches[5]}
        }
        $best = $choices | Sort-Object Major,Minor,Patch,Stage,Number -Descending | Select-Object -First 1
        if (-not $best) { throw 'No compatible CPython catalog entry found. No unofficial runtime was substituted.' }
        Status ('Installing bootstrap Python ' + $best.Version + '. Existing Python installations are retained.')
        & $uv python install $best.Key
        if ($LASTEXITCODE -ne 0) { throw 'The selected Python build failed to install; no silent stable fallback was attempted.' }
        $found = & $uv python find --managed-python $best.Key
        if ($LASTEXITCODE -ne 0) { throw 'Installed Python could not be located.' }
        $python = @($found | Where-Object { $_ -and (Test-Path -LiteralPath ([string]$_) -PathType Leaf) }) | Select-Object -Last 1
        $python = Test-Python ([string]$python) @()
        if (-not $python) { throw 'Bootstrap Python failed its execution/version check.' }
    }
    Status 'Running offline application regression tests before launch.'
    Push-Location $PSScriptRoot
    try { & $python -m unittest discover -s tests; if ($LASTEXITCODE -ne 0) { throw 'Application self-tests failed. Dashboard was not launched.' } }
    finally { Pop-Location }
    if ($NoLaunch) { Status 'NO_LAUNCH_VERIFICATION_OK'; exit 0 }
    Status 'Opening the dashboard. Keep this launcher window open until you quit the dashboard.'
    $app = Join-Path $PSScriptRoot 'app.py'
    & $python $app --root $Root
    if ($LASTEXITCODE -ne 0) { throw "The dashboard stopped with exit code $LASTEXITCODE. See Bootstrap-Diagnostic.txt." }
    exit 0
} catch {
    $msg = $_.Exception.Message
    # Do not dump environment variables, tokens, config files, or exception command lines.
    $msg = $msg.Replace($env:USERPROFILE,'[USER]')
    Status ('BOOTSTRAP FAILED: ' + $msg)
    Write-Host "Diagnostic file: $Diagnostic" -ForegroundColor Yellow
    try {
        Add-Type -AssemblyName System.Windows.Forms
        [System.Windows.Forms.MessageBox]::Show("$msg`n`nDiagnostic: $Diagnostic", 'OpenAI Edge Workbench - bootstrap issue', 'OK', 'Error') | Out-Null
    } catch { }
    exit 1
}
