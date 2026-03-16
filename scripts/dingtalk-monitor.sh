#!/bin/bash
# 钉钉消息接收监控脚本
# 检测超过阈值时间无消息时触发告警/刷新

LOG_FILE="/tmp/openclaw/dingtalk-monitor.log"
STATE_FILE="/tmp/openclaw/dingtalk-monitor-state.json"
ALERT_THRESHOLD_SEC=600  # 10 分钟无消息触发告警
CHECK_INTERVAL_SEC=60    # 每 60 秒检查一次

# 颜色输出
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

log() {
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] $1" | tee -a "$LOG_FILE"
}

# 获取 Gateway 日志中最后一条钉钉消息的时间戳
get_last_message_time() {
    local gateway_log="/tmp/openclaw/openclaw-$(date '+%Y-%m-%d').log"
    if [ -f "$gateway_log" ]; then
        local last_msg=$(grep -i "dingtalk: received message" "$gateway_log" 2>/dev/null | tail -1)
        if [ -n "$last_msg" ]; then
            # 从 JSON 日志中提取时间
            echo "$last_msg" | grep -oP '"time":"\K[^"]+' | head -1
        fi
    fi
}

# 计算时间差（秒）
time_diff_seconds() {
    local last_time="$1"
    if [ -z "$last_time" ]; then
        echo "999999"  # 无记录，返回大值
        return
    fi
    
    local last_epoch=$(date -j -f "%Y-%m-%dT%H:%M:%S.%3NZ" "$last_time" +%s 2>/dev/null)
    if [ -z "$last_epoch" ]; then
        # 尝试另一种格式
        last_epoch=$(date -j -f "%Y-%m-%dT%H:%M:%SZ" "$last_time" +%s 2>/dev/null)
    fi
    
    if [ -z "$last_epoch" ]; then
        echo "999999"
        return
    fi
    
    local now_epoch=$(date +%s)
    echo $((now_epoch - last_epoch))
}

# 发送告警消息到钉钉
send_alert() {
    local message="$1"
    log "${RED}[ALERT]${NC} $message"
    
    # 通过 openclaw message 发送告警到配置的管理员
    # 这里需要获取管理员的 dingtalk ID
    # 暂时记录日志，实际告警需要配置
}

# 主检查逻辑
check_health() {
    local last_time=$(get_last_message_time)
    local diff=$(time_diff_seconds "$last_time")
    
    # 读取上次告警时间
    local last_alert_time=0
    if [ -f "$STATE_FILE" ]; then
        last_alert_time=$(cat "$STATE_FILE" | grep -oP '"last_alert_time":\s*\K\d+' || echo "0")
    fi
    
    local now_epoch=$(date +%s)
    local alert_cooldown=1800  # 告警冷却时间 30 分钟
    
    if [ "$diff" -gt "$ALERT_THRESHOLD_SEC" ]; then
        # 超过阈值，检查是否需要告警
        local time_since_alert=$((now_epoch - last_alert_time))
        
        if [ "$time_since_alert" -gt "$alert_cooldown" ]; then
            send_alert "钉钉消息接收中断检测：已 ${diff} 秒无新消息（阈值：${ALERT_THRESHOLD_SEC}秒）"
            echo "{\"last_alert_time\": $now_epoch, \"last_check\": \"$last_time\", \"diff_seconds\": $diff}" > "$STATE_FILE"
            log "${YELLOW}[WARN]${NC} 消息接收中断，已记录告警"
        else
            log "${YELLOW}[WARN]${NC} 消息接收中断：${diff}秒（告警冷却中）"
        fi
    else
        log "${GREEN}[OK]${NC} 消息接收正常（最后消息：${diff}秒前）"
    fi
}

# 启动监控
log "=========================================="
log "钉钉消息接收监控启动"
log "告警阈值：${ALERT_THRESHOLD_SEC}秒"
log "检查间隔：${CHECK_INTERVAL_SEC}秒"
log "=========================================="

while true; do
    check_health
    sleep "$CHECK_INTERVAL_SEC"
done
