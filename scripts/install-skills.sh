#!/bin/bash

# 安装 skills 脚本 - 每 20 分钟尝试一次，直到 20:00

SKILLS=("openclaw-tavily-search" "find-skills")
WORKDIR="/Users/ssd/.openclaw/workspace"
END_TIME="20:00"

log() {
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] $1"
}

install_skill() {
    local skill=$1
    log "尝试安装：$skill"
    cd "$WORKDIR"
    if clawhub install "$skill" 2>&1; then
        log "✅ $skill 安装成功！"
        return 0
    else
        log "❌ $skill 安装失败（速率限制或其他错误）"
        return 1
    fi
}

# 主循环
while true; do
    CURRENT_TIME=$(date '+%H:%M')
    
    # 检查是否超过 20:00
    if [[ "$CURRENT_TIME" > "$END_TIME" ]]; then
        log "已超过 $END_TIME，停止尝试"
        break
    fi
    
    log "=== 开始尝试安装 skills ==="
    
    for skill in "${SKILLS[@]}"; do
        install_skill "$skill"
    done
    
    log "=== 本次尝试结束，20 分钟后再次尝试 ==="
    
    # 等待 20 分钟 (1200 秒)
    sleep 1200
done

log "脚本执行完毕"
