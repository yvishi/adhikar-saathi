<#
Opens a free Cloudflare "quick tunnel" to the Adhikar Saathi backend so
Sarvam's cloud (or any external service) can reach it, without exposing a
real phone number, paying for anything, or requiring an account/signup.

Assumes the backend is ALREADY running per RUNBOOK.md (scripts\run_demo.ps1)
on the given -Port. This script does NOT start the backend for you.

Usage:
  powershell -File scripts\tunnel.ps1
  powershell -File scripts\tunnel.ps1 -Port 8000

The printed https://*.trycloudflare.com URL is the {BASE_URL} to paste into
the Sarvam Voice Agent's HTTPS tool config (see app/voiceagent/tool_config.md).
It changes every time this script is restarted -- re-paste it each session.
Press Ctrl+C to stop the tunnel.
#>
param(
    [int]$Port = 8000
)

$ErrorActionPreference = "Stop"

function Find-Cloudflared {
    $onPath = Get-Command cloudflared -ErrorAction SilentlyContinue
    if ($onPath) { return $onPath.Source }

    $known = @(
        "$env:ProgramFiles\cloudflared\cloudflared.exe",
        "${env:ProgramFiles(x86)}\cloudflared\cloudflared.exe",
        "$env:LOCALAPPDATA\Programs\cloudflared\cloudflared.exe"
    )
    foreach ($p in $known) {
        if (Test-Path $p) { return $p }
    }
    return $null
}

$cf = Find-Cloudflared

if (-not $cf) {
    Write-Host "cloudflared not found. Install it with (no admin rights needed):" -ForegroundColor Yellow
    Write-Host "  winget install --id Cloudflare.cloudflared -e" -ForegroundColor Yellow
    Write-Host "or download the .exe directly from:" -ForegroundColor Yellow
    Write-Host "  https://github.com/cloudflare/cloudflared/releases/latest" -ForegroundColor Yellow
    exit 1
}

# Quick sanity check that something is actually listening before we tunnel to it.
$listening = Test-NetConnection -ComputerName 127.0.0.1 -Port $Port -WarningAction SilentlyContinue
if (-not $listening.TcpTestSucceeded) {
    Write-Host "Nothing is listening on 127.0.0.1:$Port yet." -ForegroundColor Yellow
    Write-Host "Start the backend first (see RUNBOOK.md), e.g.:" -ForegroundColor Yellow
    Write-Host "  powershell -File scripts\run_demo.ps1" -ForegroundColor Yellow
    exit 1
}

Write-Host "Using cloudflared at: $cf"
Write-Host "Opening a quick tunnel to http://127.0.0.1:$Port ..."
Write-Host "(free, no account, no uptime guarantee -- fine for a demo/test tunnel only)"
Write-Host ""

# cloudflared prints the public URL to stderr as an INF log line; let it
# stream straight to the console so the owner can see it appear live.
& $cf tunnel --url "http://127.0.0.1:$Port"
