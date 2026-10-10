# OpenAI Edge Workbench Implementation Plan

**Goal:** Deliver one click launcher plus inspectable source for aggressive public-release maintenance.
**Architecture:** Python engine + loopback web dashboard + PowerShell bootstrap. Isolated runtime paths and package-manager operations, incremental reports.
**Tech stack:** Python standard library >=3.11, HTML/CSS/JavaScript, Windows PowerShell 5.1, WinGet, uv, npm.
**Spec:** DESIGN.md

## Global constraints
Prefer public development releases; preserve credentials and unrelated environments; do not promise universal repairs; no background service or scheduled task is installed.

## Review focus
- Stale alpha release behind final release; version selection must not regress.
- Existing target settings differ; never overwrite silently.
- Command succeeds but actual version is absent; report not verified.
- Another webpage calls local dashboard; no mutation without same-origin session authorization.
- Installed tools are running or paths are symlinks/junctions; no forced deletion.

## Tasks
1. Write tests for pure policy/protection functions; implement engine primitives.
2. Implement package adapters, managed runtime staging, migration, smoke checks and report; test with mocked external commands and local fixture archives.
3. Implement dashboard and strictly bounded HTTP actions; test unauthenticated/invalid/cross-origin requests and successful read-only calls.
4. Package Windows bootstrap and single-file CMD; verify exact embedded payload SHA-256 and archive contents, compile Python, check JavaScript, and include explicit Windows execution limitations.
