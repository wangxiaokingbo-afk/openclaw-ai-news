#!/bin/bash
# 钉钉消息接收监控 - 分钟级检查
# 检测超过 10 分钟无消息时记录告警

LOG_FILE="/tmp/openclaw/dingtalk-monitor.log"
STATE_FILE="/tmp/openclaw/dingtalk-monitor-state.json"
ALERT_THRESHOLD_SEC=600  # 10 分钟

log() {
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] $1" >> "$LOG_FILE"
}

# 获取 Gateway 日志中最后一条钉钉消息的时间戳
gateway_log="/tmp/openclaw/openclaw-$(date '+%Y-%m-%d').log"
if [ ! -f "$gateway_log" ]; then
    log "[ERROR] Gateway 日志不存在"
    exit 0
fi

# 提取最后消息时间
last_msg=$(grep -i "dingtalk: received message" "$gateway_log" 2>/dev/null | tail -1)
if [ -z "$last_msg" ]; then
    log "[WARN] 今日无钉钉消息记录"
    exit 0
fi

# 解析时间戳 (格式：2026-03-14T12:17:32.439Z)
last_time=$(echo "$last_msg" | sed -n 's/.*"time":"\([^"]*\)".*/\1/p' | head -1)
if [ -z "$last_time" ]; then
    log "[WARN] 无法解析时间戳"
    exit 0
fi

# 计算时间差
last_epoch=$(date -j -f "%Y-%m-%dT%H:%M:%S" "${last_time%.*}" +%s 2>/dev/null)
if [ -z "$last_epoch" ]; then
    log "[WARN] 时间转换失败：$last_time"
    exit 0
fi

now_epoch=$(date +%s)
diff=$((now_epoch - last_epoch))

# 读取上次告警时间
last_alert_time=0
if [ -f "$STATE_FILE" ]; then
    last_alert_time=$(cat "$STATE_FILE" 2>/dev/null | sed -n 's/.*"last_alert_time":\s*\([0-9]*\).*/\1/p' || echo "0")
fi

alert_cooldown=1800  # 30 分钟冷却

if [ "$diff" -gt "$ALERT_THRESHOLD_SEC" ]; then
    time_since_alert=$((now_epoch - last_alert_time))
    
    if [ "$time_since_alert" -gt "$alert_cooldown" ]; then
        log "[ALERT] 消息接收中断：已 ${diff} 秒无新消息（阈值：${ALERT_THRESHOLD_SEC}秒）"
        echo "{\"last_alert_time\": $now_epoch, \"last_msg_time\": \"$last_time\", \"diff_seconds\": $diff}" > "$STATE_FILE"
    else
        log "[WARN] 消息接收中断：${diff}秒（告警冷却中）"
    fi
else
    log "[OK] 消息接收正常（最后消息：${diff}秒前）"
fi
