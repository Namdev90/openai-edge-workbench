# Short graphical launcher. The downstream downloader remains commit-pinned and SHA256 checked.
& {
    $ErrorActionPreference='Stop'
    $ProgressPreference='SilentlyContinue'
    $path=Join-Path $env:TEMP ('Namu-Setup-'+[guid]::NewGuid().ToString('N')+'.ps1')
    $oldAll=$env:EDGE_ALL_TOOLS
    try {
        Write-Host 'Downloading verified Namu AI Workbench setup...' -ForegroundColor Cyan
        Invoke-WebRequest 'https://raw.githubusercontent.com/Namdev90/openai-edge-workbench/20c323f68c15be6e91ebc4e31f173f581c940c0a/Setup.ps1' -UseBasicParsing -TimeoutSec 90 -OutFile $path
        if ((Get-FileHash -LiteralPath $path -Algorithm SHA256).Hash -ine '2360295d3d44f19d5e39ea2f48a774833720ca4d26f9b1ccb1a86c25540cdd04') { throw 'Setup checksum mismatch. Nothing executed.' }
        $env:EDGE_ALL_TOOLS='1'
        $arguments=@('-NoProfile','-STA','-ExecutionPolicy','Bypass','-File',$path)
        if ($env:EDGE_NO_LAUNCH -eq '1') { $arguments+=@('-NoLaunch','-NoShortcut') }
        if ($env:EDGE_ROOT) { $arguments+=@('-Root',$env:EDGE_ROOT) }
        Write-Host 'Checking published source and opening the graphical dashboard. Keep this window open.' -ForegroundColor Cyan
        & "$env:SystemRoot\System32\WindowsPowerShell\v1.0\powershell.exe" @arguments
        if ($LASTEXITCODE -ne 0) { throw 'Setup failed. Inspect the Workbench bootstrap diagnostic.' }
    } finally {
        $env:EDGE_ALL_TOOLS=$oldAll
        if (Test-Path -LiteralPath $path) { Remove-Item -LiteralPath $path -Force }
    }
}
