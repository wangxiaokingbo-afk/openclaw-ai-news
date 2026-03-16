# 钉钉 AI 表格导入功能 - 永久记忆

## 🎯 核心功能

**将 CSV/Excel/JSON 文件导入到钉钉 AI 表格**

## 📦 技能位置

```
skills/csv-to-ai-table/
├── SKILL.md
├── README.md
├── scripts/
│   └── import_to_table.py  # 核心脚本
└── examples/
    ├── example_data.csv
    ├── example_data.xlsx
    └── example_data.json
```

## 🚀 使用方法

### 命令行调用
```bash
python3 skills/csv-to-ai-table/scripts/import_to_table.py \
  --file data.csv \
  --name "表格名称" \
  --sheet "数据表名"
```

### Python 调用
```python
import subprocess
result = subprocess.run([
    "python3", "skills/csv-to-ai-table/scripts/import_to_table.py",
    "--file", "data.csv",
    "--name", "我的表格"
])
```

### OpenClaw sessions_spawn
```python
{
  "runtime": "subagent",
  "task": "将 data.csv 导入到 AI 表格，表格名：我的数据"
}
```

## 🔧 前置要求

1. **mcporter CLI**: `npm install -g mcporter`
2. **钉钉 MCP 配置**: `mcporter config add dingtalk-ai-table --url "<URL>"`
3. **根节点 UUID**: 保存在 `TABLE.md` 中

## 📊 支持的文件格式

| 格式 | 扩展名 | 说明 |
|------|--------|------|
| CSV | .csv | 英文逗号分隔，UTF-8 编码 |
| Excel | .xlsx, .xls | 需要 openpyxl 库 |
| JSON | .json | 对象数组格式 |

## ⚠️ 注意事项

1. **CSV 必须用英文逗号** - 中文逗号会导致字段识别错误
2. **字段类型自动推断** - number/text/singleSelect/date/user
3. **批量导入** - 默认 100 条/批次，最大 1000 条
4. **文件大小限制** - CSV 50MB / JSON 10MB

## 📝 成功案例

**小红书旅行 POI 数据**
- 文件：xhs_lx/xhs_lx/poi_final.csv
- 表格名：小红书旅行 POI 数据
- 数据表：POI 记录
- 记录数：8 条
- 状态：✅ 成功
- 表格 UUID: P0MALyR8klGKeLKeUQql7roYW3bzYmDO

## 🔗 相关文档

- 技能文档：skills/csv-to-ai-table/SKILL.md
- 使用指南：skills/csv-to-ai-table/README.md
- 钉钉 MCP: https://mcp.dingtalk.com/#/detail?mcpId=1060

---

**记录时间**: 2026-03-12 23:17
**记录人**: 小橙
