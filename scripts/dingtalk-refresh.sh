#!/bin/bash
# 钉钉 Gateway 定时刷新脚本 v2
# 修复：添加完整的环境变量

# 设置环境变量
export PATH="/Users/ssd/.npm-global/bin:/usr/local/bin:/usr/bin:/bin:/usr/sbin:/sbin"
export NODE_PATH="/Users/ssd/.npm-global/lib/node_modules"

MONITOR_LOG="/tmp/openclaw/dingtalk-refresh.log"
OPENCLAW_CMD="/Users/ssd/.npm-global/bin/openclaw"

echo "[$(date '+%Y-%m-%d %H:%M:%S')] === Gateway 定时刷新 ===" >> "$MONITOR_LOG"
echo "[$(date '+%Y-%m-%d %H:%M:%S')] PATH=$PATH" >> "$MONITOR_LOG"

# 检查 node
if ! command -v node &> /dev/null; then
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] ERROR: node not found" >> "$MONITOR_LOG"
    exit 1
fi

echo "[$(date '+%Y-%m-%d %H:%M:%S')] Restarting Gateway..." >> "$MONITOR_LOG"
$OPENCLAW_CMD gateway restart >> "$MONITOR_LOG" 2>&1

sleep 5
STATUS=$($OPENCLAW_CMD gateway status 2>&1)

if echo "$STATUS" | grep -q "RPC probe: ok"; then
    PID=$(echo "$STATUS" | grep "pid" | grep -oE '[0-9]+' | head -1)
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] ✓ Gateway restarted (PID: $PID)" >> "$MONITOR_LOG"
else
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] ✗ Restart may have failed" >> "$MONITOR_LOG"
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] Status: $STATUS" >> "$MONITOR_LOG"
fi

echo "" >> "$MONITOR_LOG"
