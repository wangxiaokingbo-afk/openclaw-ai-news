#!/bin/bash
# 小栗主动打招呼脚本
# 发送"你好"消息

export PATH="/Users/ssd/.npm-global/bin:/usr/local/bin:/usr/bin:/bin:/usr/sbin:/sbin"
export NODE_PATH="/Users/ssd/.npm-global/lib/node_modules"

LOG_FILE="/tmp/openclaw/dingtalk-hello.log"
GROUP_ID="cidwdUjqhs0Pc+p2nKu4pHyVQ=="

echo "[$(date '+%Y-%m-%d %H:%M:%S')] Sending hello..." >> "$LOG_FILE"

# 发送问候消息
MESSAGE="你好"

# 使用 openclaw message 工具发送
cd /Users/ssd/.openclaw/workspace
openclaw message send --target "$GROUP_ID" --message "$MESSAGE" >> "$LOG_FILE" 2>&1

echo "[$(date '+%Y-%m-%d %H:%M:%S')] Hello sent successfully" >> "$LOG_FILE"
echo "" >> "$LOG_FILE"
