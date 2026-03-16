#!/bin/bash
# 小栗测试推送脚本
# 17:50 验证测试

export PATH="/Users/ssd/.npm-global/bin:/usr/local/bin:/usr/bin:/bin:/usr/sbin:/sbin"
export NODE_PATH="/Users/ssd/.npm-global/lib/node_modules"

LOG_FILE="/tmp/openclaw/dingtalk-test.log"
GROUP_ID="cidwdUjqhs0Pc+p2nKu4pHyVQ=="

echo "[$(date '+%Y-%m-%d %H:%M:%S')] 测试推送开始" >> "$LOG_FILE"

# 推送内容
MESSAGE="你好，我是小栗"

# 发送消息
cd /Users/ssd/.openclaw/workspace
RESULT=$(openclaw message send --target "$GROUP_ID" --message "$MESSAGE" 2>&1)

if echo "$RESULT" | grep -q "Sent via DingTalk"; then
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] SUCCESS: 消息发送成功" >> "$LOG_FILE"
else
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] FAILED: $RESULT" >> "$LOG_FILE"
fi

echo "[$(date '+%Y-%m-%d %H:%M:%S')] 测试推送完成" >> "$LOG_FILE"
echo "" >> "$LOG_FILE"
