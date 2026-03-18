#!/bin/bash
# 热点资讯定时推送脚本 v1.5 (修复 sessions_spawn 命令)
# 执行时间：每天 09:30、12:00、18:00、23:00

set -e

export PATH="/Users/ssd/.npm-global/bin:/usr/local/bin:/usr/bin:/bin:/usr/sbin:/sbin"
export NODE_PATH="/Users/ssd/.npm-global/lib/node_modules"

LOG_FILE="/tmp/openclaw/hot-news-push.log"
WORKSPACE="/Users/ssd/.openclaw/workspace"
GROUP_ID="cidwdUjqhs0Pc+p2nKu4pHyVQ=="
TIMESTAMP=$(date '+%Y-%m-%d %H:%M:%S')
TIME_SLOT=$(date '+%H%M')
REPORT_DATE=$(date '+%Y-%m-%d')

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

# 创建任务描述文件
TASK_FILE=$(mktemp)
cat > "$TASK_FILE" << 'TASK_EOF'
【重要】执行热点资讯抓取前，必须先完成自我检查！

=====================================
🔍 自我检查清单 (必须逐项确认)
=====================================

【数据源检查 - 必须 100% 符合】
1. X 平台 40%: browser (profile="chrome", @wang9067 登录态)
   - 搜索：AI、人工智能、新能源、地缘政治、金融、投资
   - ❌ 不搜 Tesla
2. News Minimalist 30%: https://www.newsminimalist.com (significance ≥ 5.2)
3. Google 搜索 20%: web_search 工具
4. YouTube 10%: browser 抓取首页 trending 播客/新闻

【禁止项检查】
- ❌ 不用 The Verge
- ❌ 不抓个人 YouTube 频道
- ❌ 不搜 Tesla

【内容规范】
- 领域分布：AI 50% (5 条)、新能源 30% (3 条)、金融 10% (1 条)、政治 10% (1 条)
- 每条：标题 + 要点 + 锐评（10 条锐评）
- ❌ 无核心结论部分

【输出要求】
1. Markdown: daily-top10-YYYY-MM-DD-HHMM.md
2. HTML: daily-top10-YYYY-MM-DD-HHMM.html
3. git add + commit + push
4. 发送钉钉 ActionCard 到 cidwdUjqhs0Pc+p2nKu4pHyVQ==

【平台异常处理】
- 在报告中红色警告
- 降级使用 Google 搜索
- 不替换为未授权网站

=====================================
✅ 自我检查完成后，开始执行抓取
=====================================

请按照 hot-news-automation skill 规范执行。
TASK_EOF

log "启动子 agent 执行热点资讯抓取..."

# 使用 sessions_spawn 子代理执行任务
cd "$WORKSPACE"
SESSIONS_RESULT=$(sessions_spawn --runtime subagent --mode run --task "$(cat "$TASK_FILE")" --timeout 300 2>&1) || true

rm -f "$TASK_FILE"

log "子 agent 响应：$SESSIONS_RESULT"

# 检查报告是否生成
if [ -f "$WORKSPACE/reports/daily-top10-${REPORT_DATE}-${TIME_SLOT}.md" ]; then
    log "✓ 报告已生成：daily-top10-${REPORT_DATE}-${TIME_SLOT}.md"
    
    RUIPING_COUNT=$(grep -c "锐评" "$WORKSPACE/reports/daily-top10-${REPORT_DATE}-${TIME_SLOT}.md" || echo "0")
    log "✓ 锐评数量：$RUIPING_COUNT 条"
    
    if [ "$RUIPING_COUNT" -lt 10 ]; then
        log "⚠️ 警告：锐评数量不足 10 条"
    fi
    
    if [ -f "$WORKSPACE/reports/daily-top10-${REPORT_DATE}-${TIME_SLOT}.html" ]; then
        log "✓ HTML 报告已生成"
    else
        log "⚠️ 警告：HTML 报告未生成"
    fi
else
    REPORT_FILE=$(ls -t "$WORKSPACE/reports/daily-top10-${REPORT_DATE}"*.md 2>/dev/null | head -1)
    if [ -n "$REPORT_FILE" ]; then
        log "✓ 报告已生成：$(basename "$REPORT_FILE")"
        RUIPING_COUNT=$(grep -c "锐评" "$REPORT_FILE" || echo "0")
        log "✓ 锐评数量：$RUIPING_COUNT 条"
    else
        log "⚠ 未找到今日报告文件"
    fi
fi

# Git 部署
log "开始 Git 部署..."
cd "$WORKSPACE"
git add reports/daily-top10-${REPORT_DATE}-${TIME_SLOT}.md 2>/dev/null || true
git add reports/daily-top10-${REPORT_DATE}-${TIME_SLOT}.html 2>/dev/null || true

if ! git diff --cached --quiet 2>/dev/null; then
    git commit -m "🔥 Add daily top10 report ${REPORT_DATE} ${TIME_SLOT}" 2>&1 | while read line; do log "git: $line"; done
    log "Git commit 完成，推送中..."
else
    log "ℹ️ 无新文件需要提交"
fi

log "热点资讯推送任务完成"
log ""
