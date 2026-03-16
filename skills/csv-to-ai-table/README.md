# CSV/JSON 导入到钉钉 AI 表格

**通用技能**：一键将数据文件导入到钉钉 AI 表格，支持其他 agent 调用。

## 🚀 快速使用

### 基本用法

```bash
# 导入 CSV 文件
python3 skills/csv-to-ai-table/scripts/import_to_table.py \
  --file data.csv \
  --name "我的数据表格"

# 导入 JSON 文件
python3 skills/csv-to-ai-table/scripts/import_to_table.py \
  --file data.json \
  --name "销售数据"
```

### 在其他 Agent 中调用

```python
import subprocess

# 方法 1：直接调用脚本
result = subprocess.run([
    "python3", "skills/csv-to-ai-table/scripts/import_to_table.py",
    "--file", "data.csv",
    "--name", "我的表格"
], capture_output=True, text=True)

# 方法 2：使用 OpenClaw sessions_spawn
{
  "runtime": "subagent",
  "task": "将 xhs_lx/poi_verified.json 导入到 AI 表格，表格名：小红书 POI 数据"
}
```

## 📋 完整参数

```bash
python3 import_to_table.py \
  --file <文件路径> \              # 必填：CSV 或 JSON
  --name <表格名称> \              # 必填
  --sheet <数据表名> \             # 可选，默认"数据表"
  --fields '<字段配置>' \          # 可选，自动推断
  --batch-size 100 \               # 可选，默认 100
  --dry-run \                      # 可选，预览模式
  --help                           # 帮助
```

## 📊 示例数据

技能目录包含示例数据：

```bash
# CSV 示例
skills/csv-to-ai-table/examples/example_data.csv

# JSON 示例
skills/csv-to-ai-table/examples/example_data.json
```

## 🔧 前置要求

1. **安装 mcporter**: `npm install -g mcporter`
2. **配置钉钉 MCP**: `mcporter config add dingtalk-ai-table --url "<URL>"`
3. **获取根节点**: 运行一次自动创建 `TABLE.md`

## 📁 文件结构

```
skills/csv-to-ai-table/
├── SKILL.md                    # 技能说明
├── README.md                   # 本文档
├── scripts/
│   └── import_to_table.py      # 主导入脚本
└── examples/
    ├── example_data.csv        # CSV 示例
    └── example_data.json       # JSON 示例
```

## 🎯 使用场景

- ✅ 数据分析报告 → AI 表格
- ✅ 爬虫结果 → AI 表格
- ✅ 业务数据 → AI 表格
- ✅ 定时任务 → AI 表格

## 📞 调用示例

### 场景 1：小红书数据导入

```bash
python3 skills/csv-to-ai-table/scripts/import_to_table.py \
  --file xhs_lx/poi_verified_20260312.json \
  --name "小红书旅行 POI 数据"
```

### 场景 2：销售报表导入

```bash
python3 skills/csv-to-ai-table/scripts/import_to_table.py \
  --file reports/sales_2026_q1.csv \
  --name "2026 年 Q1 销售报表" \
  --sheet "销售记录"
```

### 场景 3：定时任务

```python
# 在 OpenClaw cron 中配置
{
  "schedule": {"kind": "cron", "expr": "0 9 * * *"},
  "payload": {
    "kind": "systemEvent",
    "text": "python3 skills/csv-to-ai-table/scripts/import_to_table.py --file daily.csv --name 日报表"
  }
}
```

---

**版本**: 1.0.0  
**作者**: OpenClaw Team
