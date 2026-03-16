#!/bin/bash
# 热点资讯定时推送脚本 v1.1
# 执行时间：每天 09:00、12:00、18:00、23:00
# 功能：爬取热点资讯并推送到钉钉群

set -e

export PATH="/Users/ssd/.npm-global/bin:/usr/local/bin:/usr/bin:/bin:/usr/sbin:/sbin"
export NODE_PATH="/Users/ssd/.npm-global/lib/node_modules"

LOG_FILE="/tmp/openclaw/hot-news-push.log"
WORKSPACE="/Users/ssd/.openclaw/workspace"
GROUP_ID="cidwdUjqhs0Pc+p2nKu4pHyVQ=="
TIMESTAMP=$(date '+%Y-%m-%d %H:%M:%S')
TIME_SLOT=$(date '+%H%M')

log() {
    echo "[$TIMESTAMP] $1" >> "$LOG_FILE"
    echo "[$TIMESTAMP] $1"
}

log "========================================"
log "热点资讯推送任务开始 (时段：$TIME_SLOT)"

# 检查 Gateway 状态
log "检查 Gateway 状态..."
if ! openclaw gateway status 2>&1 | grep -q "RPC probe: ok"; then
    log "ERROR: Gateway 未运行，尝试启动..."
    openclaw gateway start
    sleep 5
    if ! openclaw gateway status 2>&1 | grep -q "RPC probe: ok"; then
        log "ERROR: Gateway 启动失败，退出任务"
        exit 1
    fi
fi
log "✓ Gateway 运行正常"

# 使用 sessions_send 发送任务到子 agent
log "启动子 agent 执行热点资讯抓取..."

# 创建任务描述文件
TASK_FILE=$(mktemp)
cat > "$TASK_FILE" << 'TASK_EOF'
执行热点资讯抓取和推送任务

要求：
1. 按照 hot-news-automation skill 规范执行
2. 抓取 X 平台、News Minimalist、YouTube、Google 搜索的热点资讯
3. 按 50/30/10/10 比例筛选 (AI/新能源/商业金融/社会政治)
4. 每条资讯包含：标题 + 要点 + 锐评
5. 生成 Markdown 和 HTML 报告（版本化命名：daily-top10-YYYY-MM-DD-HHMM）
6. 部署到 GitHub Pages
7. 发送钉钉卡片消息到群聊 cidwdUjqhs0Pc+p2nKu4pHyVQ==
8. 更新时间段：当前时间

注意：
- 必须执行真实抓取，不使用模拟数据
- AI 内容排除学习/教程类
- 检查平台状态（X 平台 Cookie、News Minimalist 可访问性）
- 执行去重比对（检查 config/pushed-items.json）
- 报告结构：核心结论置顶 + 资讯详情 + 链接置底
TASK_EOF

# 通过 openclaw agent 执行任务
cd "$WORKSPACE"
RESULT=$(openclaw agent --task "$(cat "$TASK_FILE")" 2>&1) || true

rm -f "$TASK_FILE"

log "子 agent 响应：$RESULT"

# 检查报告是否生成
REPORT_DATE=$(date '+%Y-%m-%d')
if [ -f "$WORKSPACE/reports/daily-top10-${REPORT_DATE}-${TIME_SLOT}.md" ]; then
    log "✓ 报告已生成：daily-top10-${REPORT_DATE}-${TIME_SLOT}.md"
else
    # 检查是否有今日报告（可能时间戳略有不同）
    REPORT_FILE=$(ls -t "$WORKSPACE/reports/daily-top10-${REPORT_DATE}"*.md 2>/dev/null | head -1)
    if [ -n "$REPORT_FILE" ]; then
        log "✓ 报告已生成：$(basename "$REPORT_FILE")"
    else
        log "⚠ 未找到今日报告文件（子 agent 可能仍在执行）"
    fi
fi

log "热点资讯推送任务完成"
log ""
