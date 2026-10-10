# Official sources checked for this catalog — 10 October 2026

Versions are discovered at runtime; this is not a fixed-version snapshot.

- ChatGPT Windows app and current Store installation ID: https://learn.chatgpt.com/docs/windows/windows-app
- Current desktop and Classic downloads: https://chatgpt.com/download/
- Official app migration/import guidance: https://learn.chatgpt.com/docs/import
- Codex CLI and releases: https://github.com/openai/codex and https://github.com/openai/codex/releases
- Codex CLI documentation: https://learn.chatgpt.com/docs/cli
- Official API CLI: https://developers.openai.com/api/docs/libraries/openai-cli and https://github.com/openai/openai-cli
- WinGet install semantics: https://learn.microsoft.com/en-us/windows/package-manager/winget/install
- WinGet return codes: https://github.com/microsoft/winget-cli/blob/master/doc/windows/package-manager/winget/returnCodes.md
- WebView2 Evergreen distribution and official registry presence checks: https://learn.microsoft.com/en-us/microsoft-edge/webview2/concepts/distribution
- Windows network timeout error interpretation: https://learn.microsoft.com/en-us/troubleshoot/windows-client/installing-updates-features-roles/common-windows-update-errors
- Windows Terminal official releases and local signed-bundle installation: https://github.com/microsoft/terminal
- Chrome Canary WinGet manifest and required side-by-side installer switches: https://github.com/microsoft/winget-pkgs/blob/master/manifests/g/Google/Chrome/Canary/157.0.8095.0/Google.Chrome.Canary.installer.yaml
- VS Code command-line extension management: https://code.visualstudio.com/docs/configure/command-line
- uv CLI and Python catalogs: https://docs.astral.sh/uv/reference/cli/ and https://docs.astral.sh/uv/concepts/python-versions/
- Node nightly metadata and checksums: https://nodejs.org/download/nightly/index.json
- .NET installer and preview quality: https://learn.microsoft.com/en-us/dotnet/core/tools/dotnet-install-script
- Official browser extension, linked from OpenAI's download page: https://chromewebstore.google.com/detail/chatgpt/hehggadaopoacecdllhhajmbjkdcmajg
- npm official package registry: https://registry.npmjs.org/
- PyPI package index: https://pypi.org/simple/

Catalog package identity is queried using exact IDs at runtime. No missing package ID is replaced by an approximate search result. Publisher package managers may fetch dependencies from their own distribution endpoints. This utility's HTTPS allowlist applies to its own direct downloads, not to every network operation performed inside third-party installers.
