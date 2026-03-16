#!/bin/bash
# 钉钉连接探活脚本 v4 - 修复 REGISTERED 误判问题
# 变更：不再将 REGISTERED not set 视为故障，仅检测实际连接状态

export PATH="/Users/ssd/.npm-global/bin:/usr/local/bin:/usr/bin:/bin:/usr/sbin:/sbin"
export NODE_PATH="/Users/ssd/.npm-global/lib/node_modules"

MONITOR_LOG="/tmp/openclaw/dingtalk-keepalive.log"
OPENCLAW_CMD="/Users/ssd/.npm-global/bin/openclaw"
LOG_FILE="/tmp/openclaw/openclaw-$(date +%Y-%m-%d).log"

echo "[$(date '+%Y-%m-%d %H:%M:%S')] Keepalive check started" >> "$MONITOR_LOG"

# 检查 node 是否可用
if ! command -v node &> /dev/null; then
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] ERROR: node not found in PATH" >> "$MONITOR_LOG"
    exit 1
fi

# 检查 Gateway 状态
STATUS=$($OPENCLAW_CMD gateway status 2>&1)
if ! echo "$STATUS" | grep -q "RPC probe: ok"; then
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] ✗ Gateway unhealthy, restarting..." >> "$MONITOR_LOG"
    $OPENCLAW_CMD gateway restart >> "$MONITOR_LOG" 2>&1
    sleep 5
    exit 0
fi

# 检查钉钉连接状态 - 只看 connected，不看 REGISTERED
LAST_DINGTALK=$(grep "dingtalk:" "$LOG_FILE" 2>/dev/null | tail -5)

# 检查是否有连接失败或异常关闭
if echo "$LAST_DINGTALK" | grep -q "connection lost\|abnormal closure\|reconnect attempt"; then
    RECENT_FAILURES=$(grep "dingtalk:" "$LOG_FILE" 2>/dev/null | tail -20 | grep -c "connection lost\|abnormal closure")
    
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] ⚠ Connection issues detected ($RECENT_FAILURES/20)" >> "$MONITOR_LOG"
    
    if [ "$RECENT_FAILURES" -ge 5 ]; then
        echo "[$(date '+%Y-%m-%d %H:%M:%S')] ACTION: Multiple failures, full restart..." >> "$MONITOR_LOG"
        launchctl unload ~/Library/LaunchAgents/ai.openclaw.gateway.plist 2>> "$MONITOR_LOG"
        sleep 2
        pkill -f "openclaw-gateway" 2>/dev/null
        sleep 2
        launchctl load ~/Library/LaunchAgents/ai.openclaw.gateway.plist 2>> "$MONITOR_LOG"
        sleep 5
        echo "[$(date '+%Y-%m-%d %H:%M:%S')] Gateway fully restarted" >> "$MONITOR_LOG"
    else
        echo "[$(date '+%Y-%m-%d %H:%M:%S')] Monitoring... (failures=$RECENT_FAILURES)" >> "$MONITOR_LOG"
    fi
else
    # 检查是否有成功连接的日志
    if echo "$LAST_DINGTALK" | grep -q "Stream client connected\|reconnect succeeded\|WebSocket open"; then
        echo "[$(date '+%Y-%m-%d %H:%M:%S')] ✓ Connection healthy (REGISTERED flag ignored - see monitor.ts)" >> "$MONITOR_LOG"
    else
        echo "[$(date '+%Y-%m-%d %H:%M:%S')] ? Status unclear, checking Gateway..." >> "$MONITOR_LOG"
    fi
fi

echo "" >> "$MONITOR_LOG"
