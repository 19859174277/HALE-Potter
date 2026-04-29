# HALE-Potter One-Click Launcher (PowerShell)
$scriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path

Write-Host "==========================================" -ForegroundColor Cyan
Write-Host "   HALE-Potter 智库助手一键启动脚本" -ForegroundColor Cyan
Write-Host "==========================================" -ForegroundColor Cyan
Write-Host ""

# Backend
Write-Host "[1/2] 正在启动 FastAPI 后端服务..." -ForegroundColor Yellow
$backendDir = Join-Path $scriptDir "backend"
Set-Location $backendDir

if (-not (Test-Path "venv")) {
    Write-Host "检测到首次运行，正在创建 Python 虚拟环境..." -ForegroundColor DarkGray
    python -m venv venv
}

& .\venv\Scripts\Activate.ps1
pip install -q -r requirements.txt

$backendCmd = "cd `""$backendDir`""; .\venv\Scripts\python.exe -m pip install -q -r requirements.txt; .\venv\Scripts\python.exe -m uvicorn app.main:app --reload --port 8000 --host 0.0.0.0"
Start-Process powershell -ArgumentList "-NoExit", "-Command", $backendCmd -WindowStyle Normal

# Frontend
Write-Host "[2/2] 正在启动 React 前端服务..." -ForegroundColor Yellow
$frontendDir = Join-Path $scriptDir "frontend"
Set-Location $frontendDir

if (-not (Test-Path "node_modules")) {
    Write-Host "检测到首次运行，正在安装 npm 依赖..." -ForegroundColor DarkGray
    npm install
}

$frontendCmd = "cd `""$frontendDir`""; npm run dev"
Start-Process powershell -ArgumentList "-NoExit", "-Command", $frontendCmd -WindowStyle Normal

Write-Host ""
Write-Host "==========================================" -ForegroundColor Green
Write-Host "服务启动完成！" -ForegroundColor Green
Write-Host "后端 API:  http://localhost:8000" -ForegroundColor White
Write-Host "前端界面: http://localhost:5173" -ForegroundColor White
Write-Host "==========================================" -ForegroundColor Green
Write-Host ""
Write-Host "按任意键关闭此窗口（服务仍会在后台运行）..." -ForegroundColor DarkGray
$null = $Host.UI.RawUI.ReadKey("NoEcho,IncludeKeyDown")
