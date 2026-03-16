#!/bin/bash
# 钉钉定时打招呼脚本
# 每天 16:30 发送问候消息

export PATH="/Users/ssd/.npm-global/bin:/usr/local/bin:/usr/bin:/bin:/usr/sbin:/sbin"
export NODE_PATH="/Users/ssd/.npm-global/lib/node_modules"

LOG_FILE="/tmp/openclaw/dingtalk-greeting.log"
GROUP_ID="cidwdUjqhs0Pc+p2nKu4pHyVQ=="

echo "[$(date '+%Y-%m-%d %H:%M:%S')] Sending greeting..." >> "$LOG_FILE"

# 发送问候消息
MESSAGE="下午好，小万！☕️ 16:30 的定时问候已送达。今天过得怎么样？"

# 使用 openclaw message 工具发送
cd /Users/ssd/.openclaw/workspace
openclaw message send --target "$GROUP_ID" --message "$MESSAGE" >> "$LOG_FILE" 2>&1

echo "[$(date '+%Y-%m-%d %H:%M:%S')] Greeting sent successfully" >> "$LOG_FILE"
echo "" >> "$LOG_FILE"
