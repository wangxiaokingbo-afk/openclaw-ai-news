#!/bin/bash
# 小橙主动推送脚本 v2
# 功能：定时向钉钉群推送消息

export PATH="/Users/ssd/.npm-global/bin:/usr/local/bin:/usr/bin:/bin:/usr/sbin:/sbin"
export NODE_PATH="/Users/ssd/.npm-global/lib/node_modules"

LOG_FILE="/tmp/openclaw/dingtalk-push.log"
GROUP_ID="cidwdUjqhs0Pc+p2nKu4pHyVQ=="

echo "========================================" >> "$LOG_FILE"
echo "[$(date '+%Y-%m-%d %H:%M:%S')] 推送任务开始" >> "$LOG_FILE"

# 检查 Gateway 状态
if ! openclaw gateway status 2>&1 | grep -q "RPC probe: ok"; then
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] ERROR: Gateway 未运行" >> "$LOG_FILE"
    exit 1
fi

# 推送内容（可自定义）
MESSAGE="你好，小万！🍊 这是小橙的定时推送

当前时间：$(date '+%Y-%m-%d %H:%M:%S')
系统状态：正常
推送类型：定时汇报"

# 发送消息
cd /Users/ssd/.openclaw/workspace
RESULT=$(openclaw message send --target "$GROUP_ID" --message "$MESSAGE" 2>&1)

if echo "$RESULT" | grep -q "Sent via DingTalk"; then
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] SUCCESS: 消息发送成功" >> "$LOG_FILE"
else
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] FAILED: $RESULT" >> "$LOG_FILE"
fi

echo "[$(date '+%Y-%m-%d %H:%M:%S')] 推送任务完成" >> "$LOG_FILE"
echo "" >> "$LOG_FILE"
