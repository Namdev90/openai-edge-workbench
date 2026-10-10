# One-command bootstrap. Fetches source from your isolated GitHub branch.
[CmdletBinding()]
param([switch]$Scheduled,[switch]$Offline,[switch]$NoGui,[switch]$Rollback)
$ErrorActionPreference='Stop'; $ProgressPreference='SilentlyContinue'
if ($env:OS -ne 'Windows_NT') { throw 'This installer requires Windows 10/11.' }
[Net.ServicePointManager]::SecurityProtocol=[Net.SecurityProtocolType]::Tls12
$repo='Namdev90/amreye-ai'; $branch='openai-device-manager'
$root=Join-Path $env:LOCALAPPDATA 'Namu\OpenAI-Device-Manager'
$releases=Join-Path $root 'releases'
New-Item -ItemType Directory $releases -Force | Out-Null
$engine=Join-Path $env:SystemRoot 'System32\WindowsPowerShell\v1.0\powershell.exe'
$pointer=Join-Path $root 'current.json'; $lock=$null; $current=$null; $updaterNote=''
function Write-File([string]$Path,[string]$Text) { [IO.File]::WriteAllText($Path,$Text,[Text.UTF8Encoding]::new($false)) }
function Test-Payload([string]$Folder) {
    if (!(Test-Path (Join-Path $Folder 'payload-hashes.json'))) { throw 'Cached payload lacks integrity metadata.' }
    $hashes=Get-Content (Join-Path $Folder 'payload-hashes.json') -Raw | ConvertFrom-Json
    foreach ($name in @('Manager.ps1','Install.ps1','tests.ps1')) {
        $path=Join-Path $Folder $name
        if (!(Test-Path $path) -or (Get-FileHash $path -Algorithm SHA256).Hash -ne $hashes.$name) { throw "Payload checksum failed: $name" }
        $tokens=$null; $errors=$null
        [void][Management.Automation.Language.Parser]::ParseFile($path,[ref]$tokens,[ref]$errors)
        if ($errors.Count) { throw "PowerShell syntax validation failed for $name" }
    }
    & $engine -NoProfile -NonInteractive -ExecutionPolicy Bypass -File (Join-Path $Folder 'tests.ps1')
    if ($LASTEXITCODE -ne 0) { throw 'Offline core tests failed. Candidate will not be activated.' }
}
try {
    $lock=[IO.File]::Open((Join-Path $root 'updater.lock'),'OpenOrCreate','ReadWrite','None')
    if (Test-Path $pointer) { $current=Get-Content $pointer -Raw | ConvertFrom-Json }
    $selected=$null
    if ($Rollback) {
        if (!$current.previous) { throw 'No previous manager release is available.' }
        $selected=$current.previous
        if ($selected -notmatch '^[a-f0-9]{40}$') { throw 'Invalid cached release identifier.' }
        Test-Payload (Join-Path $releases $selected)
    } elseif (!$Offline) {
        try {
            Write-Host 'Checking your GitHub branch for the newest manager code...' -ForegroundColor Cyan
            $headers=@{'User-Agent'='Namu-OpenAI-Device-Manager';Accept='application/vnd.github+json'}
            $head=Invoke-RestMethod "https://api.github.com/repos/$repo/commits/$branch" -Headers $headers -TimeoutSec 30
            $sha=[string]$head.sha
            if ($sha -notmatch '^[a-f0-9]{40}$') { throw 'GitHub returned an invalid commit identifier.' }
            $folder=Join-Path $releases $sha
            $cacheValid=$false
            if (Test-Path $folder) { try { Test-Payload $folder; $cacheValid=$true } catch {} }
            if (!$cacheValid) {
                $stage=Join-Path $releases ($sha+'.staging-'+[guid]::NewGuid().ToString('N'))
                New-Item -ItemType Directory $stage -Force | Out-Null
                $hashes=[ordered]@{}
                foreach ($name in @('Manager.ps1','Install.ps1','tests.ps1')) {
                    Write-Host "Downloading and checking $name..."
                    $meta=Invoke-RestMethod "https://api.github.com/repos/$repo/contents/${name}?ref=$sha" -Headers $headers -TimeoutSec 30
                    $path=Join-Path $stage $name
                    Invoke-WebRequest "https://raw.githubusercontent.com/$repo/$sha/$name" -OutFile $path -UseBasicParsing -TimeoutSec 90
                    $bytes=[IO.File]::ReadAllBytes($path)
                    $prefix=[Text.Encoding]::UTF8.GetBytes(('blob '+$bytes.Length+[char]0))
                    $all=New-Object byte[] ($prefix.Length+$bytes.Length)
                    [Array]::Copy($prefix,0,$all,0,$prefix.Length); [Array]::Copy($bytes,0,$all,$prefix.Length,$bytes.Length)
                    $alg=[Security.Cryptography.SHA1]::Create()
                    try { $gitHash=([BitConverter]::ToString($alg.ComputeHash($all))).Replace('-','').ToLowerInvariant() } finally { $alg.Dispose() }
                    if ($gitHash -ne $meta.sha) { throw "GitHub source-object mismatch for $name" }
                    $hashes[$name]=(Get-FileHash $path -Algorithm SHA256).Hash
                }
                Write-File (Join-Path $stage 'payload-hashes.json') ($hashes | ConvertTo-Json)
                Test-Payload $stage
                if (Test-Path $folder) { Move-Item -LiteralPath $folder -Destination ($folder+'.corrupt-'+[guid]::NewGuid().ToString('N')) }
                Move-Item -LiteralPath $stage -Destination $folder
            }
            $selected=$sha
        } catch {
            $updaterNote='Update check failed; using validated cached code when available. '+$_.Exception.Message
            Write-Warning $updaterNote
            Write-File (Join-Path $root 'Updater-Last-Error.txt') $updaterNote
        }
    }
    if (!$selected) {
        if (!$current.current -or $current.current -notmatch '^[a-f0-9]{40}$') { throw 'No verified offline installation exists. Restore internet access and rerun this file.' }
        $selected=$current.current
        Test-Payload (Join-Path $releases $selected)
    }
    $previous=if ($current -and $current.current -ne $selected) { $current.current } else { $current.previous }
    $state=[ordered]@{current=$selected;previous=$previous;repository=$repo;branch=$branch;checkedUTC=(Get-Date).ToUniversalTime().ToString('o');note=$updaterNote}
    Write-File ($pointer+'.new') ($state | ConvertTo-Json)
    Move-Item -LiteralPath ($pointer+'.new') -Destination $pointer -Force
    $payload=Join-Path $releases $selected
    $boot=Join-Path $root 'Bootstrap.ps1'
    Copy-Item -LiteralPath (Join-Path $payload 'Install.ps1') -Destination ($boot+'.new') -Force
    Move-Item -LiteralPath ($boot+'.new') -Destination $boot -Force
    # Reusable desktop shortcut; no startup folder, hidden service, or credentials.
    try {
        $shell=New-Object -ComObject WScript.Shell
        $shortcut=$shell.CreateShortcut((Join-Path ([Environment]::GetFolderPath('Desktop')) 'OpenAI Device Manager.lnk'))
        $shortcut.TargetPath=$engine; $shortcut.Arguments='-NoProfile -ExecutionPolicy Bypass -STA -File "'+$boot+'"'
        $shortcut.WorkingDirectory=$root; $shortcut.Description='Preview-first OpenAI maintenance with visible logs'; $shortcut.Save()
    } catch { Write-Warning 'Desktop shortcut could not be created; the bootstrap file is still usable.' }
    $lock.Dispose(); $lock=$null
    Write-Host "Manager release $selected verified. Opening the maintenance interface..." -ForegroundColor Green
    $args=@('-NoProfile','-ExecutionPolicy','Bypass','-STA','-File',(Join-Path $payload 'Manager.ps1'),'-DataRoot',$root)
    if ($NoGui) { $args+='-NoGui' } else { $args+='-AutoStart' }
    & $engine @args
    exit $LASTEXITCODE
} catch {
    $message='BOOTSTRAP FAILED: '+$_.Exception.Message
    Write-File (Join-Path $root 'Bootstrap-Failure.txt') $message
    Write-Error $message -ErrorAction Continue
    if (!$NoGui) { Add-Type -AssemblyName System.Windows.Forms; [void][Windows.Forms.MessageBox]::Show($message+"`r`nLog: $root",'OpenAI Device Manager') }
    exit 1
} finally { if ($lock) { $lock.Dispose() } }
