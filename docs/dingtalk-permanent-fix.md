# 钉钉连接持久性 - 根治方案

_最后更新：2026-03-15 01:30_

---

## 问题诊断

### 当前状态（问题配置）

```bash
# crontab -l 输出
* * * * * /Users/ssd/.openclaw/workspace/scripts/dingtalk-monitor-check.sh
* * * * * /Users/ssd/.openclaw/workspace/scripts/dingtalk-monitor-check.sh  # 重复！
```

**问题分析**：
| 监控脚本 | 频率 | 状态 | 问题 |
|---------|------|------|------|
| `dingtalk-monitor-check.sh` | 每分钟 ×2 | ✗ 冗余 | 重复执行，浪费资源 |
| `dingtalk-monitor.sh` (LaunchAgent) | 持续 | ✗ 冲突 | 与 crontab 脚本功能重叠 |
| `dingtalk-keepalive.sh` | 每 10 分钟 | ✓ 正确 | 被其他脚本干扰 |

### 为什么会导致断开？

1. **多个脚本同时检测** → 可能同时触发重启
2. **重启竞争** → Gateway 被反复启停，连接无法稳定
3. **误判故障** → `monitor-check.sh` 检测"10 分钟无消息"即告警，但夜间本应静默

---

## 根治方案

### 步骤 1：清理冗余监控

```bash
# 1. 移除重复的 crontab 任务
crontab -l | grep -v "dingtalk-monitor-check.sh" | crontab -

# 2. 卸载 LaunchAgent
launchctl bootout gui/$(id -u) /Users/ssd/Library/LaunchAgents/dingtalk-monitor.plist 2>/dev/null
rm -f ~/Library/LaunchAgents/dingtalk-monitor.plist

# 3. 验证清理结果
crontab -l | grep dingtalk    # 应无输出
launchctl list | grep dingtalk # 应无输出
```

### 步骤 2：配置正确的保活机制

**方案 A：使用 crontab（推荐）**

```bash
# 编辑 crontab
crontab -e

# 添加以下内容（每 10 分钟探活）
*/10 * * * * /Users/ssd/.openclaw/workspace/scripts/dingtalk-keepalive.sh >> /tmp/openclaw/dingtalk-keepalive.log 2>&1

# 每日凌晨 3 点诊断报告
0 3 * * * /Users/ssd/.openclaw/workspace/scripts/dingtalk-diagnose.sh >> /tmp/openclaw/dingtalk-diagnose.log 2>&1
```

**方案 B：使用 LaunchAgent（更稳定）**

```bash
# 创建 LaunchAgent 配置文件
cat > ~/Library/LaunchAgents/ai.openclaw.dingtalk-keepalive.plist << 'EOF'
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
    <key>Label</key>
    <string>ai.openclaw.dingtalk-keepalive</string>
    
    <key>ProgramArguments</key>
    <array>
        <string>/bin/bash</string>
        <string>/Users/ssd/.openclaw/workspace/scripts/dingtalk-keepalive.sh</string>
    </array>
    
    <key>WorkingDirectory</key>
    <string>/Users/ssd/.openclaw/workspace</string>
    
    <key>StandardOutPath</key>
    <string>/tmp/openclaw/dingtalk-keepalive-stdout.log</string>
    
    <key>StandardErrorPath</key>
    <string>/tmp/openclaw/dingtalk-keepalive-stderr.log</string>
    
    <key>StartInterval</key>
    <integer>600</integer>  <!-- 600 秒 = 10 分钟 -->
    
    <key>RunAtLoad</key>
    <true/>
</dict>
</plist>
EOF

# 加载 LaunchAgent
launchctl load ~/Library/LaunchAgents/ai.openclaw.dingtalk-keepalive.plist
```

### 步骤 3：验证修复

```bash
# 1. 检查 Gateway 状态
openclaw gateway status

# 2. 运行诊断
/Users/ssd/.openclaw/workspace/scripts/dingtalk-diagnose.sh

# 3. 查看保活日志（等待 10 分钟后）
tail -20 /tmp/openclaw/dingtalk-keepalive.log

# 4. 确认无冗余监控
crontab -l | grep -c "dingtalk-monitor-check"  # 应为 0
launchctl list | grep dingtalk                   # 应无 monitor 相关
```

---

## 预期效果

| 指标 | 修复前 | 修复后 |
|------|--------|--------|
| 监控脚本数量 | 3 套冲突 | 1 套 |
| 检查频率 | 每分钟（过度） | 每 10 分钟 |
| 误判重启 | 频繁 | 极少 |
| 连接稳定性 | 断续 | 持久 |

---

## 监控与告警

### 日志位置

```bash
# 保活日志
tail -f /tmp/openclaw/dingtalk-keepalive.log

# Gateway 日志
tail -f /tmp/openclaw/openclaw-$(date +%Y-%m-%d).log

# 诊断报告（每日生成）
cat /tmp/openclaw/dingtalk-diagnose.log
```

### 健康检查标准

| 日志关键字 | 含义 | 处理 |
|-----------|------|------|
| `Stream client connected` | 连接正常 | ✓ 忽略 |
| `WebSocket open` | 连接正常 | ✓ 忽略 |
| `REGISTERED not set` | 正常现象 | ✓ **忽略**（不要误判） |
| `connection lost` | 连接断开 | ⚠ 记录 |
| `abnormal closure` | 异常关闭 | ⚠ 记录 |
| `reconnect succeeded` | 重连成功 | ✓ 正常 |

### 何时需要干预

只有出现以下情况才需要手动处理：

1. **连续 3 次以上** `connection lost` 且未自动恢复
2. Gateway 进程消失（`openclaw gateway status` 显示 not running）
3. 超过 30 分钟无法收发消息

---

## 一键修复脚本

创建修复脚本自动执行上述步骤：

```bash
#!/bin/bash
# ~/openclaw/workspace/scripts/dingtalk-fix-permanent.sh

echo "=== 钉钉连接根治修复 ==="

# 1. 清理 crontab
echo "[1/4] 清理冗余 crontab 任务..."
crontab -l 2>/dev/null | grep -v "dingtalk-monitor-check.sh" | crontab -

# 2. 卸载旧 LaunchAgent
echo "[2/4] 卸载旧监控服务..."
launchctl bootout gui/$(id -u) ~/Library/LaunchAgents/dingtalk-monitor.plist 2>/dev/null
rm -f ~/Library/LaunchAgents/dingtalk-monitor.plist

# 3. 安装新保活服务
echo "[3/4] 安装新保活服务..."
cat > ~/Library/LaunchAgents/ai.openclaw.dingtalk-keepalive.plist << 'EOF'
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
    <key>Label</key>
    <string>ai.openclaw.dingtalk-keepalive</string>
    <key>ProgramArguments</key>
    <array>
        <string>/bin/bash</string>
        <string>/Users/ssd/.openclaw/workspace/scripts/dingtalk-keepalive.sh</string>
    </array>
    <key>WorkingDirectory</key>
    <string>/Users/ssd/.openclaw/workspace</string>
    <key>StartInterval</key>
    <integer>600</integer>
    <key>RunAtLoad</key>
    <true/>
</dict>
</plist>
EOF
launchctl load ~/Library/LaunchAgents/ai.openclaw.dingtalk-keepalive.plist

# 4. 验证
echo "[4/4] 验证修复..."
echo ""
echo "=== Gateway 状态 ==="
openclaw gateway status | grep -E "Runtime|RPC"
echo ""
echo "=== 活跃监控服务 ==="
launchctl list | grep -i "dingtalk\|openclaw" || echo "无"
echo ""
echo "✓ 修复完成！等待 10 分钟后检查保活日志"
```

---

## 后续优化建议

### 1. 网络层优化

如果仍有偶发断开，可能是网络问题：

```bash
# 检查网络稳定性
ping -c 10 oapi.dingtalk.com

# 检查 DNS 解析
nslookup oapi.dingtalk.com
```

### 2. Gateway 配置优化

```json
// ~/.openclaw/openclaw.json
{
  "gateway": {
    "port": 18789,
    "reconnectInterval": 5000,      // 重连间隔 5 秒
    "maxReconnectAttempts": -1,     // 无限重试
    "heartbeatInterval": 30000      // 心跳 30 秒
  }
}
```

### 3. 长期监控

建议运行一周观察：
- 每天断开次数 < 3 次 → 正常
- 每天断开次数 > 10 次 → 需要进一步排查

---

## 常见问题

**Q: 为什么不能检测"无消息"作为故障？**
A: 钉钉是推送机制，夜间或空闲时段本应无消息。用"无消息"判断故障会导致误重启。

**Q: REGISTERED not set 是什么意思？**
A: 钉钉 Stream SDK 的正常行为。官方文档明确说明该标志"may not always be set"，但连接仍可正常工作。

**Q: 可以完全关闭监控吗？**
A: 不建议。钉钉连接可能因网络波动断开，需要保活脚本自动恢复。

---

_执行修复后，请观察 24-48 小时，如有问题查看日志并联系。_
