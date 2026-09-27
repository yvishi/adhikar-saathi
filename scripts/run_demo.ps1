# Start the Adhikar Saathi demo server. Run from anywhere:  powershell -File scripts\run_demo.ps1 [-Mock] [-Port 8000] [-Verify]
#   default : real Sarvam (needs SARVAM_API_KEY in .env), TTS cache on, judge/debug info on
#   -Mock   : no network, canned answers built from the real cards, silent audio
#   -Verify : adds a second LLM check that the answer is supported by the cards (slower, about 2x LLM cost)
param([switch]$Mock, [int]$Port = 8000, [switch]$Verify)
$root = Split-Path -Parent $PSScriptRoot
Set-Location $root
$env:LLM_PROVIDER = "sarvam"
$env:RETRIEVAL_MODE = "topk"
$env:DEBUG_RESPONSES = "1"
$env:TTS_CACHE = "1"
$env:PYTHONIOENCODING = "utf-8"
if ($Mock) { $env:MOCK_MODE = "1" } else { Remove-Item Env:MOCK_MODE -ErrorAction SilentlyContinue }
if ($Verify) { $env:VERIFY = "1" }
Write-Host "Open http://127.0.0.1:$Port/  (mock=$($Mock.IsPresent))"
python -m uvicorn app.backend.main:app --host 127.0.0.1 --port $Port
