# HALE-Potter 全球健康资源寻优与政策决策智库助手

HALE-Potter 是一个面向卫生政策制定者、国际发展研究人员和公共卫生精算师的 AI Agent 应用。系统基于全球 190 国健康系统底座数据，通过多维雷达诊断与 MO-QPO 线性规划寻优，自动生成高规格政策研报。

## 核心特性

- **多轮对话界面**：仿 ChatGPT 的对话流，支持历史记录与追问
- **实时状态机反馈**：展示 NER → Radar → Sankey → Policy → Report 全流程
- **硬核工具调用**：复用 `Tool_1` 生成 6 维雷达图，`Tool_2` 生成 Pareto 资源重组桑基图
- **智库研报自动落盘**：将图表与 Kimi 生成的政策文本通过 `docxtpl` 注入 Word 模板
- **流式渲染**：对话框内即时展示雷达图与桑基图
- **数据透视页**：查看底层 CSV 排名与指标详情
- **配置页**：管理 Kimi API Key 与模型参数（α, β）

## 技术栈

- **前端**：React (Vite) + Tailwind CSS + Lucide Icons
- **后端**：Python (FastAPI) + SQLite
- **AI 接入**：Kimi (Moonshot) Code API（Anthropic 兼容层）
- **绘图**：Matplotlib（非交互式 Agg 后端）
- **研报**：docxtpl

## 项目结构

```
HALE_Potter/
├── frontend/          # React 前端
├── backend/           # FastAPI 后端
│   ├── app/
│   │   ├── main.py
│   │   ├── routers/   # API 路由
│   │   ├── services/  # 业务逻辑（Kimi、NER、Tool、Report）
│   │   ├── models/    # 数据库与 Schema
│   │   └── utils/     # 校验工具
│   └── requirements.txt
├── start_all.bat      # Windows 一键启动
├── start_all.sh       # Unix 一键启动
├── Tool_1_Radar_Diagnosis.py
├── Tool_2_Sankey_Optimizer.py
├── GH_Copilot_Knowledge_Base_Final.csv
├── 模版.docx
├── HALE_Potter.PNG
└── User.PNG
```

## 快速开始

### 环境要求

- Python 3.10+
- Node.js 18+

### 一键启动（推荐）

**Windows:**
```powershell
.\start_all.bat
```

**macOS / Linux:**
```bash
chmod +x start_all.sh
./start_all.sh
```

脚本会自动创建 Python 虚拟环境、安装依赖并启动前后端服务。

### 手动启动

**1. 启动后端**
```bash
cd backend
python -m venv venv
# Windows: venv\Scripts\activate
# Unix:    source venv/bin/activate
pip install -r requirements.txt
uvicorn app.main:app --reload --port 8000
```

**2. 启动前端**
```bash
cd frontend
npm install
npm run dev
```

**3. 访问应用**

打开浏览器访问：http://localhost:5173

## 首次配置

1. 打开前端界面，点击左侧「系统配置」
2. 填入您的 **Kimi Code API Key**（格式：`sk-kimi-...`）
3. 默认 Base URL 为 `https://api.kimi.com/coding/`，模型固定为 `kimi-k2.5`
4. 可调整 α（效率权重）与 β（摩擦系数）以改变 MO-QPO 寻优行为
5. 点击「保存配置」

## 使用方式

在看板页的输入框中输入国家名称，例如：

- "生成中国的健康寻优方案"
- "看看印度的卫生体系"
- "分析日本的资源配置"

Agent 会自动：
1. 识别国家实体（NER）
2. 生成 Radar 6 维基准画像
3. 执行 MO-QPO 线性规划与 Sankey 资源重组流向图
4. 调用 Kimi 撰写结构化政策建议
5. 生成可下载的 Word 研报

若输入内容未包含国家名，Agent 将直接以智库专家身份进行自由问答。

## API 端点

| 端点 | 方法 | 说明 |
|---|---|---|
| `/api/chat/stream` | POST | SSE 流式对话（核心） |
| `/api/chat/sessions` | GET | 获取会话列表 |
| `/api/chat/history/{id}` | GET | 获取会话历史 |
| `/api/tools/run/{iso}` | POST | 触发 Radar + Sankey |
| `/api/reports/generate` | POST | 生成 Word 研报 |
| `/api/reports/download/{id}` | GET | 下载研报 |
| `/api/data/countries` | GET | 数据透视查询 |
| `/api/config` | GET/POST | 配置管理 |

## 资产文件校验

后端启动时会自动检查根目录下是否存在以下文件：

- `GH_Copilot_Knowledge_Base_Final.csv`
- `Tool_1_Radar_Diagnosis.py`
- `Tool_2_Sankey_Optimizer.py`
- `模版.docx`
- `HALE_Potter.PNG`
- `User.PNG`

任一缺失将导致启动失败并提示清单。

## 线程安全与并发

- 绘图任务（Matplotlib）通过 `asyncio.to_thread` 投入独立线程池执行，避免阻塞 FastAPI 主事件循环
- 图表输出采用 `Radar_{ISO}_{session_id}.png` 命名，消除多会话并发时的文件碰撞
- 后台定时任务每 30 分钟清理超过 24 小时的临时图片与报告文件

## 模型参数说明

| 参数 | 默认值 | 含义 |
|---|---|---|
| `alpha` | 0.5517 | 资金配置对因果弹性 (CATE) 的敏感系数 |
| `beta` | 0.0125 | 部门间资源重组的二次摩擦惩罚系数 |

## 许可证

本项目仅供学术研究与政策分析参考使用。
