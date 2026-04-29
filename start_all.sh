#!/bin/bash
echo "=========================================="
echo "   HALE-Potter 智库助手一键启动脚本"
echo "=========================================="
echo ""

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# Start Backend
echo "[1/2] 正在启动 FastAPI 后端服务..."
cd "$SCRIPT_DIR/backend"
if [ ! -d "venv" ]; then
    echo "检测到首次运行，正在创建 Python 虚拟环境..."
    python3 -m venv venv
fi
source venv/bin/activate
pip install -q -r requirements.txt
uvicorn app.main:app --reload --port 8000 --host 0.0.0.0 &
BACKEND_PID=$!

# Start Frontend
echo "[2/2] 正在启动 React 前端服务..."
cd "$SCRIPT_DIR/frontend"
if [ ! -d "node_modules" ]; then
    echo "检测到首次运行，正在安装 npm 依赖..."
    npm install
fi
npm run dev &
FRONTEND_PID=$!

echo ""
echo "=========================================="
echo "服务启动完成！"
echo "后端 API:  http://localhost:8000"
echo "前端界面: http://localhost:5173"
echo "=========================================="
echo ""
echo "按 Ctrl+C 停止所有服务"
wait $BACKEND_PID $FRONTEND_PID
