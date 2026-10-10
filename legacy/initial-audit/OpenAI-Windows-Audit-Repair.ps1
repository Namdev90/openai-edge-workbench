# OpenAI Windows Audit & Repair v1.0 - 2026-10-10
# Windows PowerShell 5.1+ / PowerShell 7+. No elevation required by default.
# READ FIRST: No automatic uninstall, credential reset, project dependency rewrite,
#              or modification of existing MCP server configurations.
# Usage:
#   .\OpenAI-Windows-Audit-Repair.ps1                       # Audit only
#   .\OpenAI-Windows-Audit-Repair.ps1 -Apply                # Update detected OpenAI apps, Codex npm and editor extension
#   .\OpenAI-Windows-Audit-Repair.ps1 -Apply -InstallMissing  # Also add Codex CLI/VS Code extension, when possible
#   .\OpenAI-Windows-Audit-Repair.ps1 -Apply -UseBeta       # Prefer npm beta where publisher offers one
#   .\OpenAI-Windows-Audit-Repair.ps1 -Apply -UpdatePythonSDK # Also update OpenAI packages in default Python interpreter
#   .\OpenAI-Windows-Audit-Repair.ps1 -Apply -UpdateDependencies # Also update installed VS Code and Node LTS via winget
#   .\OpenAI-Windows-Audit-Repair.ps1 -TestCodexLive # OPTIONAL: tiny authenticated Codex smoke test; uses model quota
[CmdletBinding()]
param(
    [switch]$Apply,
    [switch]$UseBeta,
    [switch]$InstallMissing,
    [switch]$UpdatePythonSDK,
    [switch]$UpdateDependencies,
    [switch]$SkipNetwork,
    [switch]$TestCodexLive
)

$ErrorActionPreference = 'Continue'
$ProgressPreference = 'SilentlyContinue'
$script:RunId = (Get-Date).ToUniversalTime().ToString('yyyyMMdd-HHmmss')
$script:OutputDir = Join-Path ([Environment]::GetFolderPath('Desktop')) "OpenAI-Audit-$script:RunId"
if (-not (Test-Path -LiteralPath ([Environment]::GetFolderPath('Desktop')))) {
    $script:OutputDir = Join-Path $env:TEMP "OpenAI-Audit-$script:RunId"
}
New-Item -ItemType Directory -Path $script:OutputDir -Force | Out-Null
$script:Notices = [System.Collections.ArrayList]::new()
$script:Actions = [System.Collections.ArrayList]::new()
$script:Warnings = [System.Collections.ArrayList]::new()
$script:Packages = [System.Collections.ArrayList]::new()
$script:Endpoints = [System.Collections.ArrayList]::new()
$script:Products = [System.Collections.ArrayList]::new()

function Add-Notice([string]$Area, [string]$State, [string]$Detail) {
    [void]$script:Notices.Add([ordered]@{ area=$Area; state=$State; detail=$Detail })
    Write-Host "[$State] $Area - $Detail"
}
function Add-Warning([string]$Msg) {
    [void]$script:Warnings.Add($Msg)
    Write-Host "[REVIEW] $Msg" -ForegroundColor Yellow
}
function Has-Exe([string]$Name) { return [bool](Get-Command $Name -ErrorAction SilentlyContinue) }
function Preferred-Exe([string[]]$Names) {
    foreach ($n in $Names) {
        $cmd = Get-Command $n -ErrorAction SilentlyContinue | Select-Object -First 1
        if ($null -ne $cmd) { return $cmd.Source }
    }
    return $null
}
function Invoke-Tool([string]$Executable, [string[]]$ArgsList) {
    if ([string]::IsNullOrWhiteSpace($Executable)) { return @{ ok=$false; code=-999; output='Executable not found' } }
    try {
        $out = & $Executable @ArgsList 2>&1 | Out-String
        $exit = $LASTEXITCODE
        if ($null -eq $exit) { $exit = 0 }
        return @{ ok=($exit -eq 0); code=[int]$exit; output=[string]$out }
    } catch {
        return @{ ok=$false; code=-998; output=$_.Exception.Message }
    }
}
function Record-Action([string]$Area, [string]$CommandLabel, [bool]$Success) {
    $s = if ($Success) { 'OK' } else { 'FAILED' }
    [void]$script:Actions.Add([ordered]@{ area=$Area; action=$CommandLabel; result=$s })
    if ($Success) { Write-Host "[COMMAND OK] $Area : $CommandLabel" -ForegroundColor Green }
    else { Add-Warning("$Area update failed or not applicable ($CommandLabel). Inspect package manager manually.") }
}
function Get-CodexVersion([string]$Exe) {
    if (!$Exe) { return 'not-on-PATH' }
    $r = Invoke-Tool $Exe @('--version')
    if ($r.ok -and $r.output -match '(\d+\.\d+\.\d+(?:[-.][a-zA-Z0-9.-]+)?)') { return $Matches[1] }
    return 'unknown'
}
function Get-PipVersion([string]$PythonExe, [string]$PackageName) {
    if (!$PythonExe) { return $null }
    $r = Invoke-Tool $PythonExe @('-m','pip','show',$PackageName)
    if ($r.ok -and $r.output -match '(?im)^Version:\s*([^\s]+)') { return $Matches[1] }
    return $null
}
function Get-RegistryInventory {
    $result = @()
    $roots = @('HKCU:\Software\Microsoft\Windows\CurrentVersion\Uninstall\*',
               'HKLM:\Software\Microsoft\Windows\CurrentVersion\Uninstall\*',
               'HKLM:\Software\WOW6432Node\Microsoft\Windows\CurrentVersion\Uninstall\*')
    foreach ($root in $roots) {
        try {
            $result += @(Get-ItemProperty -Path $root -ErrorAction SilentlyContinue |
                Where-Object { $_.DisplayName -match '(?i)ChatGPT|OpenAI|Codex' } |
                Select-Object DisplayName, DisplayVersion, Publisher)
        } catch { }
    }
    return @($result | Sort-Object DisplayName,DisplayVersion -Unique)
}
function Get-AppxInventory {
    try { return @(Get-AppxPackage -ErrorAction SilentlyContinue |
        Where-Object { $_.Name -match '(?i)OpenAI|ChatGPT|Codex' } |
        Select-Object Name,Version,Publisher) } catch { return @() }
}
function Get-NpmOpenAIPackages([string]$NpmExe) {
    $items = @()
    if (!$NpmExe) { return $items }
    $r = Invoke-Tool $NpmExe @('list','--global','--depth=0','--json')
    try {
        $parsed = $r.output | ConvertFrom-Json -ErrorAction Stop
        if ($parsed.dependencies) {
            foreach ($d in $parsed.dependencies.PSObject.Properties) {
                if ($d.Name -match '^@openai/' -or $d.Name -eq 'openai') {
                    $items += [pscustomobject]@{ name=$d.Name; current=[string]$d.Value.version }
                }
            }
        }
    } catch { Add-Warning 'Could not parse npm global package inventory.' }
    return @($items)
}
function Should-UseNpmBeta($Tags) {
    if (-not $Tags.beta) { return $false }
    if (-not $Tags.latest) { return $true }
    $b = [regex]::Match($Tags.beta, '^\d+\.\d+\.\d+')
    $l = [regex]::Match($Tags.latest, '^\d+\.\d+\.\d+')
    if (!$b.Success -or !$l.Success) { return $false }
    try { return ([version]$b.Value -gt [version]$l.Value) } catch { return $false }
}
function Get-NpmTags([string]$NpmExe, [string]$PackageName) {
    $tags = @{ latest=''; beta=''; next=''; alpha=''; canary='' }
    $r = Invoke-Tool $NpmExe @('view', $PackageName, 'dist-tags','--json')
    if ($r.ok) {
        try {
            $json = $r.output | ConvertFrom-Json -ErrorAction Stop
            foreach ($t in @('latest','beta','next','alpha','canary')) {
                if ($json.PSObject.Properties.Name -contains $t) { $tags[$t] = [string]$json.$t }
            }
        } catch { Add-Warning "Could not parse release tags for $PackageName." }
    } else { Add-Warning "Could not check npm release tags for $PackageName (offline or registry issue)." }
    return $tags
}
function Get-EditorExtension([string]$EditorExe) {
    $r = Invoke-Tool $EditorExe @('--list-extensions','--show-versions')
    if (!$r.ok) { return 'list-error' }
    $match = @($r.output -split "`r?`n" | Where-Object { $_ -match '(?i)^openai\.chatgpt(@|$)' })
    if ($match.Count -eq 0) { return 'not-installed' }
    return ($match[0].Trim())
}
function Test-Service([string]$Area, [string]$Url) {
    try {
        $r = Invoke-WebRequest -Uri $Url -Method Head -UseBasicParsing -TimeoutSec 12 -MaximumRedirection 5 -ErrorAction Stop
        $code = [int]$r.StatusCode
        [void]$script:Endpoints.Add([ordered]@{ name=$Area; reachable=$true; httpStatus=$code })
        Add-Notice $Area 'REACHABLE' "HTTP $code (not an authentication test)"
    } catch {
        $code = 0
        if ($_.Exception.Response) {
            try { $code = [int]$_.Exception.Response.StatusCode } catch { }
        }
        if ($code -ge 200 -and $code -lt 500) {
            [void]$script:Endpoints.Add([ordered]@{ name=$Area; reachable=$true; httpStatus=$code })
            Add-Notice $Area 'REACHABLE' "HTTP $code (authentication/authorization not established)"
        } else {
            [void]$script:Endpoints.Add([ordered]@{ name=$Area; reachable=$false; httpStatus=$code })
            Add-Warning "$Area is not reachable over HTTPS in this check (HTTP $code)."
        }
    }
}
function Test-LocalPort([int]$Port) {
    $tcp = New-Object System.Net.Sockets.TcpClient
    try {
        $async = $tcp.BeginConnect('127.0.0.1', $Port, $null, $null)
        if (-not $async.AsyncWaitHandle.WaitOne(900)) { return $false }
        $tcp.EndConnect($async)
        return $tcp.Connected
    } catch { return $false } finally { $tcp.Close() }
}

Write-Host "`nOpenAI Windows Audit & Repair (run $script:RunId)" -ForegroundColor Cyan
Write-Host ('MODE: ' + $(if ($Apply) { 'Apply safe, supported upgrades' } else { 'Read-only audit' }))
if ($UseBeta) { Add-Warning 'Beta channel requested for npm; preview builds may be less stable than release.' }
if ($InstallMissing -and !$Apply) { Add-Warning '-InstallMissing only takes effect with -Apply.' }
if ($UpdatePythonSDK -and !$Apply) { Add-Warning '-UpdatePythonSDK only takes effect with -Apply.' }

# Step 1: System/app inventory
$os = Get-CimInstance Win32_OperatingSystem -ErrorAction SilentlyContinue
$osLabel = if ($os) { 'Windows ' + [string]$os.Version + ' / ' + [string]$os.OSArchitecture } else { 'Windows (details unavailable)' }
Add-Notice 'System' 'INFO' $osLabel
$appxBefore = @(Get-AppxInventory)
$regBefore = @(Get-RegistryInventory)
foreach ($x in $appxBefore) { [void]$script:Products.Add([ordered]@{ source='WindowsApp'; name=[string]$x.Name; version=[string]$x.Version }) }
foreach ($x in $regBefore) { [void]$script:Products.Add([ordered]@{ source='InstalledProgram'; name=[string]$x.DisplayName; version=[string]$x.DisplayVersion }) }
Add-Notice 'OpenAI Windows app packages' 'FOUND' "$($appxBefore.Count) MSIX packages, $($regBefore.Count) registry programs"

foreach ($grp in @($regBefore | Group-Object DisplayName | Where-Object { $_.Count -gt 1 })) {
    Add-Warning "Possible duplicate installed program: $($grp.Name) ($($grp.Count) versions). Manual review only."
}
foreach ($grp in @($appxBefore | Group-Object Name | Where-Object { $_.Count -gt 1 })) {
    Add-Warning "Possible side-by-side Windows app: $($grp.Name). Do not automatically remove a package."
}

$winget = Preferred-Exe @('winget.exe','winget')
$npm = Preferred-Exe @('npm.cmd','npm.exe','npm')
$node = Preferred-Exe @('node.exe','node')
$python = Preferred-Exe @('py.exe','python.exe','python')
$codex = Preferred-Exe @('codex.exe','codex.cmd','codex')
$editors = @(
    [pscustomobject]@{ name='VS Code'; exe=(Preferred-Exe @('code.cmd','code.exe','code')) },
    [pscustomobject]@{ name='VS Code Insiders'; exe=(Preferred-Exe @('code-insiders.cmd','code-insiders.exe','code-insiders')) },
    [pscustomobject]@{ name='Cursor'; exe=(Preferred-Exe @('cursor.cmd','cursor.exe','cursor')) },
    [pscustomobject]@{ name='Windsurf'; exe=(Preferred-Exe @('windsurf.cmd','windsurf.exe','windsurf')) }
)
$runtimeVersions = [ordered]@{ node='not-installed'; npm='not-installed'; python='not-installed' }
if ($node) { $r=Invoke-Tool $node @('--version'); if ($r.ok) { $runtimeVersions.node=$r.output.Trim() } }
if ($npm) { $r=Invoke-Tool $npm @('--version'); if ($r.ok) { $runtimeVersions.npm=$r.output.Trim() } }
if ($python) { $r=Invoke-Tool $python @('--version'); if ($r.ok) { $runtimeVersions.python=$r.output.Trim() } }
Add-Notice 'Package managers' 'INFO' "winget=$([bool]$winget) npm=$([bool]$npm) Python=$([bool]$python)"
Add-Notice 'Dependencies' 'INFO' "Node=$($runtimeVersions.node); npm=$($runtimeVersions.npm); Python=$($runtimeVersions.python)"
$codexVersionBefore = Get-CodexVersion $codex
if (!$winget) { Add-Warning 'winget not on PATH. Repair/install Microsoft App Installer from Microsoft Store.' }
if (!$npm) { Add-Warning 'npm not on PATH. Codex npm upgrades unavailable; native Codex may still work.' }

# Step 2: Windows managed upgrades - only detected OpenAI app names
if ($winget) {
    $available = Invoke-Tool $winget @('list','--upgrade-available','--accept-source-agreements')
    if ($available.ok -or $available.output) {
        $hits = @($available.output -split "`r?`n" | Where-Object { $_ -match '(?i)ChatGPT|OpenAI|Codex|Visual Studio Code|Node\.js' })
        Add-Notice 'winget upgrade candidates' 'INFO' "$($hits.Count) relevant rows; review report to distinguish app and dependency upgrades"
        foreach ($line in $hits) {
            # Inventory only: avoid exposing unrelated apps, machine paths or raw data in pasted report.
            if ($line -match '(?i)ChatGPT|OpenAI|Codex') { Add-Notice 'winget OpenAI candidate' 'INFO' ($line.Trim() -replace '\s{2,}', ' | ') }
        }
    } else { Add-Warning 'winget could not retrieve available upgrades.' }
    if ($Apply -and !$SkipNetwork) {
        foreach ($item in @(@{name='ChatGPT'; pattern='(?i)chatgpt'}, @{name='Codex';pattern='(?i)codex'})) {
            $installed = @($appxBefore | Where-Object { $_.Name -match $item.pattern -and $_.Name -match '(?i)openai|chatgpt' })
            if ($installed.Count -eq 0) { continue }
            # Winget upgrades if available. Lack of update is not a failure.
            $r = Invoke-Tool $winget @('upgrade','--name',$item.name,'--exact','--accept-source-agreements','--accept-package-agreements')
            if ($r.ok) { Record-Action 'Windows apps' ("winget upgrade $($item.name)") $true }
            else { Add-Notice 'Windows apps' 'CHECK' "Check $($item.name) in Microsoft Store Library > Get updates if winget did not apply an update." }
        }
        if ($UpdateDependencies) {
            if (@($editors | Where-Object { $_.name -eq 'VS Code' -and $_.exe }).Count -gt 0) {
                $r = Invoke-Tool $winget @('upgrade','--id','Microsoft.VisualStudioCode','--exact','--accept-source-agreements','--accept-package-agreements')
                if ($r.ok) { Record-Action 'VS Code' 'winget stable upgrade' $true }
                else { Add-Notice 'VS Code' 'CHECK' 'No upgrade applied by winget; may already be current.' }
            }
            if ($node) {
                $r = Invoke-Tool $winget @('upgrade','--id','OpenJS.NodeJS.LTS','--exact','--accept-source-agreements','--accept-package-agreements')
                if ($r.ok) { Record-Action 'Node LTS' 'winget upgrade' $true }
                else { Add-Notice 'Node LTS' 'CHECK' 'No upgrade applied by winget; may use a different Node manager.' }
            }
        }
    }
}

# Step 3: npm inventory / upgrade only installed official OpenAI packages
$npmPackagesBefore = @(Get-NpmOpenAIPackages $npm)
foreach ($pkg in $npmPackagesBefore) {
    $tags = @{ latest=''; beta=''; next=''; alpha=''; canary='' }
    if ($npm -and !$SkipNetwork) { $tags = Get-NpmTags $npm $pkg.name }
    [void]$script:Packages.Add([ordered]@{
        ecosystem='npm-global'; name=$pkg.name; installed=$pkg.current;
        stable=$tags.latest; beta=$tags.beta; next=$tags.next; alpha=$tags.alpha; canary=$tags.canary
    })
    Add-Notice "npm $($pkg.name)" 'FOUND' "Installed $($pkg.current); stable $($tags.latest); beta $($tags.beta)"
    if ($Apply -and !$SkipNetwork) {
        $tag = 'latest'
        if ($UseBeta -and (Should-UseNpmBeta $tags)) { $tag = 'beta' }
        elseif ($UseBeta) { Add-Notice "npm $($pkg.name)" 'CHECK' 'Beta is absent or older than stable; using stable to prevent downgrade.' }
        $r = Invoke-Tool $npm @('install','--global',"$($pkg.name)@$tag")
        Record-Action "npm $($pkg.name)" "Update to $tag" $r.ok
    }
}
if ($codex -and @($npmPackagesBefore | Where-Object { $_.name -eq '@openai/codex' }).Count -eq 0) {
    Add-Warning 'Codex exists but is not npm-managed; it may be a standalone binary. Avoid installing a competing copy.'
    if ($Apply -and !$SkipNetwork) {
        $r = Invoke-Tool $codex @('update')
        if ($r.ok) { Record-Action 'Standalone Codex' 'codex update' $true }
        else {
            $r = Invoke-Tool $codex @('--upgrade')
            if ($r.ok) { Record-Action 'Standalone Codex' 'codex --upgrade (legacy)' $true }
            else { Add-Notice 'Standalone Codex' 'CHECK' 'Self-update unsupported or failed. Use the official standalone Windows installer after manual review.' }
        }
    }
}
if (!$codex -and $InstallMissing -and $Apply -and $npm -and !$SkipNetwork) {
    $tag = 'latest'
    if ($UseBeta) {
        $tags = Get-NpmTags $npm '@openai/codex'
        if (Should-UseNpmBeta $tags) { $tag = 'beta' }
    }
    $r = Invoke-Tool $npm @('install','--global',"@openai/codex@$tag")
    Record-Action 'Codex CLI' "Install via npm ($tag)" $r.ok
}
if ($npm -and $Apply -and !$SkipNetwork) {
    $cache = Invoke-Tool $npm @('cache','verify')
    Record-Action 'npm cache' 'Verify and reclaim invalid/unnecessary cached data' $cache.ok
}

# Step 4: IDE extensions - no blanket extension updates or removals
$editorStates = [System.Collections.ArrayList]::new()
foreach ($ed in $editors) {
    if (!$ed.exe) { continue }
    $pre = Get-EditorExtension $ed.exe
    if ($Apply -and !$SkipNetwork -and ($pre -ne 'not-installed' -or $InstallMissing) -and $pre -ne 'list-error') {
        $r = Invoke-Tool $ed.exe @('--install-extension','OpenAI.chatgpt')
        Record-Action "$($ed.name) Codex extension" 'Install/update stable extension' $r.ok
    }
    $post = Get-EditorExtension $ed.exe
    [void]$editorStates.Add([ordered]@{ editor=$ed.name; before=$pre; after=$post })
    Add-Notice "$($ed.name) Codex extension" 'INFO' $post
    if ($post -eq 'not-installed') { Add-Notice $ed.name 'OPTIONAL' 'Codex extension not installed.' }
    if ($post -eq 'list-error') { Add-Warning "$($ed.name): editor extension list failed." }
}

# Step 5: Post-update Codex, identity, shadowing and MCP config
$codex = Preferred-Exe @('codex.exe','codex.cmd','codex')
$codexVersion = Get-CodexVersion $codex
$codexAuth = 'not-checked'
if ($codex) {
    $r = Invoke-Tool $codex @('login','status')
    if ($r.ok -and $r.output -match '(?i)Logged in using ChatGPT') { $codexAuth='ChatGPT sign-in configured' }
    elseif ($r.ok -and $r.output -match '(?i)(API key|logged in)') { $codexAuth='some authentication configured' }
    else { $codexAuth='not confirmed - sign in manually with codex login' }
}
$allCodex = @(Get-Command codex -All -ErrorAction SilentlyContinue | Where-Object { $_.CommandType -in @('Application','ExternalScript') })
$codexDirs = @($allCodex | ForEach-Object {
    try { (Split-Path $_.Source -Parent).TrimEnd('\') } catch { '' }
} | Where-Object { $_ } | Sort-Object -Unique)
if ($codexDirs.Count -gt 1) { Add-Warning "Codex command found in $($codexDirs.Count) different directories. An older binary may shadow the updated one; manual removal after testing." }
Add-Notice 'Codex CLI' 'INFO' "Version: $codexVersion; login: $codexAuth"

$codexHome = if ($env:CODEX_HOME) { $env:CODEX_HOME } else { Join-Path $HOME '.codex' }
$toml = Join-Path $codexHome 'config.toml'
$mcpNames = @()
$configExists = Test-Path -LiteralPath $toml
if ($configExists) {
    try {
        # Read server names only. NEVER copy secrets, tokens, auth.json or config text to report.
        $configText = Get-Content -LiteralPath $toml -ErrorAction Stop
        $mcpNames = @($configText | ForEach-Object {
            if ($_ -match '^\s*\[mcp_servers\.([^.\]]+)\]') { $Matches[1] }
        } | Where-Object { $_ } | Sort-Object -Unique)
    } catch { Add-Warning 'Could not inspect Codex MCP server headings in config.toml.' }
}
Add-Notice 'Codex MCP' 'INFO' "$($mcpNames.Count) configured server(s); connection/authentication must be verified inside Codex."
if (@($mcpNames | Where-Object { $_ -match '(?i)openaiDeveloperDocs' }).Count -eq 0 -and $codex) {
    Add-Notice 'OpenAI Docs MCP' 'OPTIONAL' 'Official read-only documentation MCP not configured. Can add later with: codex mcp add openaiDeveloperDocs --url https://developers.openai.com/mcp'
}

# Step 5b: Codex doctor and an OPTIONAL live model smoke test
$codexDoctor = 'not-checked'
$codexLive = 'not-requested (may consume model quota)'
if ($codex) {
    $r = Invoke-Tool $codex @('doctor','--json')
    if ($r.ok) { $codexDoctor='doctor command completed (inspect degraded checks inside Codex if necessary)' }
    else {
        $r = Invoke-Tool $codex @('doctor')
        if ($r.ok) { $codexDoctor='doctor command completed' }
        else { $codexDoctor='doctor unavailable or failed' }
    }
    Add-Notice 'Codex doctor' 'INFO' $codexDoctor
    if ($TestCodexLive -and !$SkipNetwork) {
        $smokeDir = Join-Path $env:TEMP "codex-smoke-$script:RunId"
        New-Item -ItemType Directory -Path $smokeDir -Force | Out-Null
        $replyPath = Join-Path $smokeDir 'final-reply.txt'
        $r = Invoke-Tool $codex @('exec','--cd',$smokeDir,'--skip-git-repo-check','--sandbox','read-only',
            '--ephemeral','--ignore-user-config','--output-last-message',$replyPath,
            'Respond with exactly: CONNECTION_OK. Do not inspect files, execute tools, or include anything else.')
        $reply = ''
        if (Test-Path -LiteralPath $replyPath) { $reply = (Get-Content -LiteralPath $replyPath -Raw -ErrorAction SilentlyContinue).Trim() }
        if ($r.ok -and $reply -eq 'CONNECTION_OK') { $codexLive='pass (authenticated model round trip)' }
        else { $codexLive='failed (inspect login, entitlements, network or model configuration)' }
        Add-Notice 'Codex live smoke test' 'INFO' $codexLive
        Remove-Item -LiteralPath $smokeDir -Recurse -Force -ErrorAction SilentlyContinue
    }
}

# Step 6: Python SDK (do not modify virtual environments automatically)
$pythonInstalled = [System.Collections.ArrayList]::new()
if ($python) {
    foreach ($p in @('openai','openai-agents')) {
        $before = Get-PipVersion $python $p
        if ($before) {
            if ($Apply -and $UpdatePythonSDK -and !$SkipNetwork) {
                $r = Invoke-Tool $python @('-m','pip','install','--upgrade',$p)
                Record-Action "Python $p" 'Upgrade in default interpreter ONLY' $r.ok
            }
            $after = Get-PipVersion $python $p
            [void]$pythonInstalled.Add([ordered]@{ name=$p; before=$before; after=$after })
            Add-Notice "Python $p" 'INFO' "Before $before; after $after"
        }
    }
    Add-Notice 'Python SDK coverage' 'LIMIT' 'Only default Python interpreter checked. Conda, uv, venv, pipx and project environments require per-project checks.'
}

# Step 7: local related tools and optional port 8787
$helperNames = @('rtk','headroom','caveman','antigravity','uv','pipx','git','pnpm','yarn')
$helpers = [System.Collections.ArrayList]::new()
foreach ($name in $helperNames) {
    $found = [bool](Get-Command $name -ErrorAction SilentlyContinue)
    [void]$helpers.Add([ordered]@{ name=$name; found=$found })
}
# Probe OpenAI's newer standalone CLI without touching authentication.
$openaiCli = Preferred-Exe @('openai.exe','openai.cmd','openai')
$openaiCliVersion = 'not-on-PATH'
if ($openaiCli) {
    $v = Invoke-Tool $openaiCli @('--version')
    if ($v.ok) { $openaiCliVersion = ($v.output -split "`r?`n" | Select-Object -First 1).Trim() }
    else { $openaiCliVersion = 'present; --version not supported or unknown' }
    Add-Notice 'Standalone OpenAI CLI' 'INFO' $openaiCliVersion
    Add-Notice 'Standalone OpenAI CLI' 'CHECK' 'If old Python CLI shadows the current Go-based CLI, inspect command locations manually.'
}
# PWA shortcuts are named entries only; no browser cookies/profile files are read.
$pwaShortcuts = @()
foreach ($root in @(
    (Join-Path $env:APPDATA 'Microsoft\Windows\Start Menu\Programs'),
    (Join-Path $env:USERPROFILE 'Desktop')) ) {
    if (Test-Path -LiteralPath $root) {
        try { $pwaShortcuts += @(Get-ChildItem -LiteralPath $root -Recurse -File -Filter '*.lnk' -ErrorAction SilentlyContinue |
            Where-Object { $_.BaseName -match '(?i)ChatGPT|Codex|OpenAI' } | Select-Object -ExpandProperty BaseName) }
        catch { }
    }
}
$pwaShortcuts = @($pwaShortcuts | Sort-Object -Unique)
if ($pwaShortcuts.Count -gt 0) { Add-Notice 'Browser/Start menu shortcuts' 'INFO' "$($pwaShortcuts.Count) ChatGPT/Codex/OpenAI shortcut names found; a browser PWA is not necessarily a duplicate app." }
$port8787 = Test-LocalPort 8787
if ($port8787) { Add-Notice 'Local proxy port 8787' 'REACHABLE' 'TCP listener detected (does not guarantee a correct service)' }
else { Add-Notice 'Local proxy port 8787' 'INFO' 'No TCP listener; relevant only if your proxy is supposed to be running.' }

# Step 8: public HTTPS connectivity (not account-authorization or paid API calls)
if (!$SkipNetwork) {
    Test-Service 'ChatGPT web' 'https://chatgpt.com/'
    Test-Service 'OpenAI public status page' 'https://status.openai.com/'
    Test-Service 'OpenAI API' 'https://api.openai.com/v1/models'
    Test-Service 'OpenAI sign-in' 'https://auth.openai.com/'
    Test-Service 'Official developer docs MCP' 'https://developers.openai.com/mcp'
    Test-Service 'npm registry' 'https://registry.npmjs.org/@openai%2fcodex'
    Test-Service 'VS Code extensions marketplace' 'https://marketplace.visualstudio.com/'
}

# Step 9: create safe, machine-readable report
$afterAppx = @(Get-AppxInventory)
$afterRegistry = @(Get-RegistryInventory)
$afterNpm = @(Get-NpmOpenAIPackages $npm)
$runReport = [ordered]@{
    audit='OpenAI Windows Audit and Repair'; schema='openai-windows-audit-v1';
    utc=(Get-Date).ToUniversalTime().ToString('o');
    mode=$(if ($Apply) { 'apply' } else { 'audit-only' });
    betaRequested=[bool]$UseBeta;
    os=$osLabel;
    apps=@($afterAppx | ForEach-Object { [ordered]@{ name=[string]$_.Name; version=[string]$_.Version } });
    otherOpenAIPrograms=@($afterRegistry | ForEach-Object { [ordered]@{ name=[string]$_.DisplayName; version=[string]$_.DisplayVersion } });
    codex=[ordered]@{ before=$codexVersionBefore; version=$codexVersion; auth=$codexAuth; separateExecutableDirectories=$codexDirs.Count; codexConfigExists=[bool]$configExists; mcpNames=@($mcpNames); doctor=$codexDoctor; liveTest=$codexLive };
    npmGlobalBefore=@($script:Packages.ToArray());
    npmGlobalAfter=@($afterNpm | ForEach-Object { [ordered]@{ name=$_.name; version=$_.current } });
    editors=@($editorStates.ToArray());
    pythonDefault=@($pythonInstalled.ToArray());
    runtimes=$runtimeVersions;
    helpers=@($helpers.ToArray());
    localPort8787Listening=[bool]$port8787;
    openaiCLI=$openaiCliVersion; browserShortcutNames=@($pwaShortcuts);
    endpoints=@($script:Endpoints.ToArray());
    actions=@($script:Actions.ToArray());
    warnings=@($script:Warnings.ToArray());
    findings=@($script:Notices.ToArray());
    notes=@(
      'Successful HTTP reachability does not establish cloud login or plugin authorization.',
      'The optional Codex live test uses a model call and consumes quota or billable tokens depending on authentication.',
      'No ChatGPT data, accounts, plugins, MCP configurations, project dependencies, VS Code profiles or older installations were deleted.',
      'Beta use is opt-in and applies only to npm packages with a beta dist-tag newer than stable; avoids downgrades.',
      'Cloud ChatGPT plugins, Google/Slack integrations and synchronization need signed-in checks.',
      'Do not paste credentials, auth.json, full config.toml or private files into chat.'
    )
}
$jsonFile = Join-Path $script:OutputDir 'Paste-Into-ChatGPT.json'
$textFile = Join-Path $script:OutputDir 'Paste-Into-ChatGPT.txt'
$json = $runReport | ConvertTo-Json -Depth 10
[System.IO.File]::WriteAllText($jsonFile, $json, [System.Text.UTF8Encoding]::new($false))
$finalText = "=== BEGIN OPENAI WINDOWS AUDIT ===`r`n" + $json + "`r`n=== END OPENAI WINDOWS AUDIT ===`r`n"
[System.IO.File]::WriteAllText($textFile, $finalText, [System.Text.UTF8Encoding]::new($false))

Write-Host "`n=================== RESULT ===================" -ForegroundColor Cyan
Write-Host "Mode: $(if ($Apply) {'APPLY'} else {'AUDIT ONLY'}) | Successful upgrade/maintenance commands: $(@($script:Actions | Where-Object { $_.result -eq 'OK' }).Count) | Warnings/review: $($script:Warnings.Count)"
Write-Host "Codex: $codexVersion | Auth: $codexAuth | Windows apps: $($afterAppx.Count) | MCP configurations: $($mcpNames.Count)"
Write-Host 'The script never uninstalls an app, removes your accounts, or deletes project versions.'
Write-Host "Report: $textFile" -ForegroundColor Green
Write-Host 'Copy the contents of Paste-Into-ChatGPT.txt and paste them into your ChatGPT conversation.' -ForegroundColor Cyan
Write-Host '================================================'
Write-Output $finalText