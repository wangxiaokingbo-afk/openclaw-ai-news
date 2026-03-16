#!/bin/bash
# 钉钉连接诊断脚本 v1
# 用途：快速诊断钉钉连接问题，输出详细状态报告

export PATH="/Users/ssd/.npm-global/bin:/usr/local/bin:/usr/bin:/bin:/usr/sbin:/sbin"

LOG_FILE="/tmp/openclaw/openclaw-$(date +%Y-%m-%d).log"
CONFIG_FILE=~/.openclaw/openclaw.json

echo "======================================"
echo "  钉钉连接诊断报告"
echo "  时间：$(date '+%Y-%m-%d %H:%M:%S')"
echo "======================================"
echo ""

# 1. Gateway 状态
echo "【1】Gateway 状态"
openclaw gateway status 2>&1 | grep -E "Runtime|RPC probe|Listening"
echo ""

# 2. 钉钉配置
echo "【2】钉钉配置"
if [ -f "$CONFIG_FILE" ]; then
    echo "配置文件：$CONFIG_FILE"
    cat "$CONFIG_FILE" | grep -A 5 '"dingtalk"' | head -10
else
    echo "配置文件未找到：$CONFIG_FILE"
fi
echo ""

# 3. 最近连接日志
echo "【3】最近连接日志 (最后 10 条)"
if [ -f "$LOG_FILE" ]; then
    grep "dingtalk:" "$LOG_FILE" 2>/dev/null | tail -10 | sed 's/^{.*"1":"//' | sed 's/".*$//'
else
    echo "日志文件未找到：$LOG_FILE"
fi
echo ""

# 4. 连接健康检查
echo "【4】连接健康检查"
CONNECTED=$(grep "dingtalk:" "$LOG_FILE" 2>/dev/null | tail -20 | grep -c "Stream client connected\|reconnect succeeded")
LOST=$(grep "dingtalk:" "$LOG_FILE" 2>/dev/null | tail -20 | grep -c "connection lost")
REGISTERED=$(grep "dingtalk:" "$LOG_FILE" 2>/dev/null | tail -20 | grep -c "REGISTERED not set")

echo "  - 成功连接次数 (20 条内): $CONNECTED"
echo "  - 连接丢失次数 (20 条内): $LOST"
echo "  - REGISTERED not set 次数: $REGISTERED"
echo ""

if [ "$LOST" -gt 3 ]; then
    echo "  ⚠ 警告：连接频繁丢失，可能需要检查网络或钉钉机器人配置"
elif [ "$CONNECTED" -gt 0 ]; then
    echo "  ✓ 连接状态正常"
else
    echo "  ? 状态不明确，请检查日志"
fi
echo ""

# 5. 保活任务状态
echo "【5】保活任务状态"
crontab -l 2>/dev/null | grep dingtalk || echo "  未配置钉钉保活 crontab"
echo ""

# 6. 保活日志
echo "【6】最近保活日志 (最后 5 条)"
if [ -f "/tmp/openclaw/dingtalk-keepalive.log" ]; then
    tail -5 /tmp/openclaw/dingtalk-keepalive.log
else
    echo "  保活日志未找到"
fi
echo ""

echo "======================================"
echo "  诊断完成"
echo "======================================"
