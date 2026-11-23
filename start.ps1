$ErrorActionPreference = 'Stop'
Set-Location -LiteralPath $PSScriptRoot
if (-not (Test-Path -LiteralPath '.env')) {
    Copy-Item -LiteralPath '.env.example' -Destination '.env'
}
$taskPython = 'python'
if (Test-Path -LiteralPath '.venv\Scripts\python.exe') {
    $taskPython = Join-Path $PSScriptRoot '.venv\Scripts\python.exe'
}
if (-not (Test-Path -LiteralPath 'dist\index.html')) {
    throw 'Please run npm install and npm run build first. See README_zh-CN.md.'
}
& $taskPython server.py
