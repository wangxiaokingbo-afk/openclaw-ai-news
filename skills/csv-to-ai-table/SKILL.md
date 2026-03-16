---
name: csv-to-ai-table
description: 通用技能：将 CSV/JSON 文件导入到钉钉 AI 表格。支持自动创建表格、智能识别字段、批量导入记录。其他 agent 可通过 sessions_spawn 或直接调用此技能实现数据表格化。
version: 1.0.0
metadata:
  openclaw:
    requires:
      env:
        - DINGTALK_MCP_URL
      bins:
        - mcporter
    primaryEnv: DINGTALK_MCP_URL
    homepage: https://github.com/openclaw/openclaw
---

# CSV/JSON 文件导入到钉钉 AI 表格

**通用技能**：任何 agent 都可以调用此技能，将数据文件快速导入到钉钉 AI 表格。

## 📦 使用场景

- 数据分析报告 → AI 表格
- 爬虫抓取结果 → AI 表格
- 业务数据导出 → AI 表格
- 定时任务数据 → AI 表格

## 🚀 快速开始

### 方式一：直接调用（推荐）

```bash
# 基本用法
python3 skills/csv-to-ai-table/scripts/import_to_table.py \
  --file data.csv \
  --name "我的数据表格"

# 指定字段
python3 skills/csv-to-ai-table/scripts/import_to_table.py \
  --file data.json \
  --name "销售数据" \
  --sheet "销售记录" \
  --fields '[{"name":"日期","type":"date"},{"name":"金额","type":"number"}]'
```

### 方式二：通过 agent 调用

```python
# 在其他 agent 中调用
from pathlib import Path
import subprocess

def import_to_ai_table(file_path, table_name):
    script = Path("skills/csv-to-ai-table/scripts/import_to_table.py")
    result = subprocess.run(
        ["python3", str(script), "--file", str(file_path), "--name", table_name],
        capture_output=True,
        text=True
    )
    return result.stdout
```

### 方式三：使用 OpenClaw sessions_spawn

```python
# 在 OpenClaw 中 spawn 子 agent 执行
{
  "runtime": "subagent",
  "task": "将 xhs_lx/poi_verified.json 导入到 AI 表格，表格名：小红书 POI 数据",
  "agentId": "csv-to-ai-table"
}
```

## 📋 输入要求

### CSV 文件格式

```csv
序号，姓名，年龄，城市，状态
1,张三，25，北京，✅ 活跃
2,李四，30，上海，⚠️ 待审核
3,王五，28，广州，❌ 已关闭
```

**要求**：
- 第一行必须是表头（字段名）
- UTF-8 编码
- 逗号分隔（支持引号包裹）

### JSON 文件格式

**格式 A：对象数组（推荐）**
```json
[
  {"序号": 1, "姓名": "张三", "年龄": 25, "城市": "北京"},
  {"序号": 2, "姓名": "李四", "年龄": 30, "城市": "上海"}
]
```

**格式 B：包含 data 字段**
```json
{
  "data": [
    {"序号": 1, "姓名": "张三"},
    {"序号": 2, "姓名": "李四"}
  ]
}
```

## 🔧 脚本参数

```bash
python3 scripts/import_to_table.py \
  --file <文件路径> \              # 必填：CSV 或 JSON 文件
  --name <表格名称> \              # 必填：AI 表格名称
  --sheet <数据表名> \             # 可选：默认"数据表"
  --fields <字段配置> \            # 可选：自动推断或手动指定
  --batch-size <批次大小> \        # 可选：默认 100，最大 1000
  --dry-run \                      # 可选：只预览不执行
  --help                           # 查看帮助
```

### 字段类型支持

| 类型 | 说明 | 自动推断规则 |
|------|------|-------------|
| `text` | 文本 | 默认类型 |
| `number` | 数字 | 列中所有值都是数字 |
| `singleSelect` | 单选 | 列中重复出现的状态值（如✅/❌） |
| `date` | 日期 | 识别日期格式（YYYY-MM-DD） |
| `user` | 人员 | 列名包含"负责人"/"用户"等 |

## 📊 完整示例

### 示例 1：导入小红书 POI 数据

```bash
python3 scripts/import_to_table.py \
  --file xhs_lx/poi_verified_20260312.json \
  --name "小红书旅行 POI 数据" \
  --sheet "POI 记录" \
  --fields '[
    {"name":"序号","type":"number"},
    {"name":"疑似 POI 名称","type":"text"},
    {"name":"城市","type":"text"},
    {"name":"热度","type":"number"},
    {"name":"状态","type":"singleSelect"}
  ]'
```

### 示例 2：导入销售数据

```bash
python3 scripts/import_to_table.py \
  --file sales_2026.csv \
  --name "2026 年销售数据" \
  --sheet "销售记录"
```

### 示例 3：预览模式（不实际创建）

```bash
python3 scripts/import_to_table.py \
  --file data.csv \
  --name "测试表格" \
  --dry-run
```

## 🔌 在其他 Agent 中集成

### 方法 1：直接调用脚本

```python
# 在你的 agent 代码中
import subprocess
import json

def create_ai_table_from_data(data, table_name):
    # 1. 保存数据到临时文件
    temp_file = "/tmp/data.json"
    with open(temp_file, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    
    # 2. 调用导入脚本
    script = "skills/csv-to-ai-table/scripts/import_to_table.py"
    result = subprocess.run(
        ["python3", script, "--file", temp_file, "--name", table_name],
        capture_output=True,
        text=True
    )
    
    # 3. 解析结果
    if result.returncode == 0:
        return {"success": True, "message": result.stdout}
    else:
        return {"success": False, "error": result.stderr}
```

### 方法 2：使用 sessions_spawn

```python
# 在 OpenClaw 主 agent 中
{
  "action": "sessions_spawn",
  "runtime": "subagent",
  "task": """
  请将以下数据导入到钉钉 AI 表格：
  - 文件：data/sales_report.json
  - 表格名：销售报表_2026Q1
  - 数据表：销售记录
  """,
  "mode": "run"
}
```

### 方法 3：导入 Python 模块

```python
# 直接导入技能中的工具函数
import sys
sys.path.append('skills/csv-to-ai-table/scripts')

from import_to_table import import_file_to_table

result = import_file_to_table(
    file_path="data.csv",
    table_name="我的表格",
    sheet_name="数据表"
)

print(f"导入成功：{result['success']}")
print(f"记录数：{result['record_count']}")
```

## ⚙️ 前置要求

### 1. 安装 mcporter

```bash
npm install -g mcporter
```

### 2. 配置钉钉 MCP

```bash
# 获取 Streamable HTTP URL
# 访问：https://mcp.dingtalk.com/#/detail?mcpId=1060

# 添加配置
mcporter config add dingtalk-ai-table --url "<你的 Streamable_HTTP_URL>"
```

### 3. 验证配置

```bash
mcporter config list
# 应显示 dingtalk-ai-table 配置
```

## 🔒 安全说明

| 安全措施 | 说明 |
|----------|------|
| **路径沙箱** | 文件路径限制在 OPENCLAW_WORKSPACE 内 |
| **文件类型白名单** | 仅允许 .csv / .json |
| **文件大小限制** | CSV 最大 50MB，JSON 最大 10MB |
| **命令超时** | mcporter 命令超时 120 秒 |
| **输入验证** | UUID 格式、字段类型白名单 |

## 📁 文件结构

```
skills/csv-to-ai-table/
├── SKILL.md                 # 技能说明（本文件）
├── README.md                # 详细文档
├── scripts/
│   ├── import_to_table.py   # 主导入脚本
│   └── table_utils.py       # 工具函数
├── examples/
│   ├── example_data.csv     # 示例 CSV
│   └── example_data.json    # 示例 JSON
└── tests/
    └── test_import.py       # 测试脚本
```

## 🐛 常见问题

### Q1: 提示"Missing appKey/appSecret"
**A**: 需要配置钉钉 MCP Server，参考"前置要求"部分。

### Q2: 导入后字段类型不对
**A**: 使用 `--fields` 参数手动指定字段类型。

### Q3: 记录导入失败
**A**: 检查数据格式，确保 JSON/CSV 格式正确；查看错误日志。

### Q4: 如何在定时任务中使用？
**A**: 在 cron job 中调用脚本即可：
```bash
# OpenClaw cron 配置
{
  "schedule": {"kind": "cron", "expr": "0 9 * * *"},
  "payload": {
    "kind": "systemEvent",
    "text": "python3 skills/csv-to-ai-table/scripts/import_to_table.py --file data/daily.csv --name 日报表"
  }
}
```

## 📞 技术支持

- **技能仓库**: https://github.com/openclaw/openclaw
- **问题反馈**: 在 OpenClaw 社区提问
- **文档**: 查看 README.md 获取详细说明

---

**版本**: 1.0.0  
**作者**: OpenClaw Team  
**许可**: MIT
