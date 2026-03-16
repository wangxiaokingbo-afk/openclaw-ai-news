# 钉钉连接断开问题 - 系统性解决方案

## 问题现象
- 钉钉连接时不时断开（早上好的，下午就断了）
- 重启 Gateway 后暂时恢复，但几小时后再次失效
- 日志显示：`dingtalk: WebSocket open, REGISTERED not set`

## 根本原因

### 1. 技术层面
- **REGISTERED 状态丢失**：钉钉 stream 连接需要回调注册，重连后状态未恢复
- **会话 TTL 过期**：钉钉服务器端会话有过期时间，客户端无感知
- **缺少健康检查**：没有主动检测连接有效性

### 2. OpenClaw 插件缺陷
- 重连逻辑只重建 WebSocket，未重新注册回调
- 没有定期心跳/健康检查机制
- 没有 REGISTERED 状态监控

---

## 解决方案

### 方案 A：立即修复（临时）

```bash
# 重启 Gateway
openclaw gateway restart

# 验证连接
openclaw gateway status
```

### 方案 B：自动监控 + 重启（推荐）

创建 cron 任务，每 30 分钟检查并自动恢复：

```bash
# 编辑 crontab
crontab -e

# 添加以下任务（每 30 分钟检查一次）
*/30 * * * * /Users/ssd/.npm-global/bin/openclaw gateway status | grep -q "RPC probe: ok" || /Users/ssd/.npm-global/bin/openclaw gateway restart
```

### 方案 C：切换到 Webhook 模式（长期）

Stream 模式有固有缺陷，建议切换到 Webhook 模式：

1. 在钉钉开发者后台配置回调 URL
2. 修改 `openclaw.json`：
```json
{
  "channels": {
    "dingtalk": {
      "accounts": {
        "default": {
          "connectionMode": "webhook",  // 改为 webhook
          ...
        }
      }
    }
  }
}
```

### 方案 D：向 OpenClaw 提交 Issue

问题已定位到钉钉插件的重连逻辑，建议提交 Issue：
- 仓库：https://github.com/openclaw/openclaw
- 标签：bug, dingtalk, websocket

---

## 监控脚本

创建监控脚本 `/Users/ssd/.openclaw/workspace/scripts/dingtalk-monitor.sh`：

```bash
#!/bin/bash
LOG_FILE="/tmp/openclaw/openclaw-$(date +%Y-%m-%d).log"

# 检查最后一条钉钉日志
LAST_DINGTALK=$(grep "dingtalk:" "$LOG_FILE" | tail -1)

# 检查是否有 REGISTERED not set
if echo "$LAST_DINGTALK" | grep -q "REGISTERED not set"; then
    echo "[$(date)] WARNING: DingTalk REGISTERED not set" >> /tmp/dingtalk-monitor.log
    
    # 检查持续时间（如果连续 5 次都是这个状态，重启）
    COUNT=$(grep "REGISTERED not set" "$LOG_FILE" | tail -10 | wc -l)
    if [ "$COUNT" -ge 5 ]; then
        echo "[$(date)] Restarting Gateway..." >> /tmp/dingtalk-monitor.log
        openclaw gateway restart
    fi
else
    echo "[$(date)] OK: DingTalk connection healthy" >> /tmp/dingtalk-monitor.log
fi
```

---

## 执行计划

### 立即执行
- [ ] 重启 Gateway 恢复当前连接
- [ ] 创建监控脚本

### 今天内
- [ ] 配置 cron 自动监控
- [ ] 测试监控脚本有效性

### 本周内
- [ ] 评估切换到 Webhook 模式
- [ ] 向 OpenClaw 提交 Issue

---

## 验证方法

```bash
# 1. 检查 Gateway 状态
openclaw gateway status

# 2. 查看实时日志
tail -f /tmp/openclaw/openclaw-*.log | grep dingtalk

# 3. 发送测试消息
# 在钉钉中发消息给机器人，看是否响应

# 4. 检查 REGISTERED 状态
grep "REGISTERED" /tmp/openclaw/openclaw-*.log | tail -5
```

---

## 联系人
- OpenClaw 社区：https://discord.com/invite/clawd
- 文档：https://docs.openclaw.ai
