# 钉钉消息接收中断调查

## 问题描述
用户报告 20:13 发送的钉钉消息"怎么全是 wired 媒体，x 平台呢"未收到回复

## 日志分析

### 时间线

| 时间 (UTC+8) | 事件 | 类型 | 会话 ID |
|-------------|------|------|---------|
| 20:04:19 | 收到消息："你验证下，我无法访问该页面..." | 群聊 | cidwdUjqhs0Pc+p2nKu4pHyVQ== |
| 20:04:19 | dispatching to agent | - | agent:main:dingtalk:group:... |
| 20:08:55 | dispatch complete (replies=5) | - | - |
| **20:13:xx** | **用户声称发送"怎么全是 wired 媒体，x 平台呢"** | **❌ 日志无记录** | **?** |
| 20:14:49 | 收到 webchat 消息"在吗" | webchat | - |
| 20:15:01 | 收到 webchat 消息"钉钉通道又断开了？" | webchat | - |
| 20:17:32 | 收到钉钉消息"在吗" | **私聊 (p2p)** | cid73FNtCqLHAfpubWojavHACuG/n+CYkVgWdCQNlOUJpw= |
| 20:17:36 | 回复"在的，小万。有什么需要我处理的吗？" | 私聊 | - |
| 20:18:05 | Gateway 重启 | - | - |
| 20:19:25 | Gateway 启动完成 | - | - |

### 关键发现

1. **20:13 的消息在日志中完全不存在**
   - 没有 `received message` 记录
   - 没有 `dispatching to agent` 记录
   - 说明钉钉服务器从未推送该消息到 Gateway

2. **20:17:32 收到私聊消息，不是群聊**
   - 用户可能切换了对话窗口
   - 群聊和私聊是不同的会话

3. **20:18:05 Gateway 重启**
   - 可能是手动执行了 `dingtalk-refresh.sh`
   - 重启期间消息可能丢失

## 可能原因

### 原因 1：钉钉 Stream 回调推送失败 ⭐⭐⭐
- Stream SDK 的 WebSocket 连接显示"connected"但实际不推送
- 钉钉服务器端推送队列积压或丢弃
- 网络波动导致推送中断

### 原因 2：消息发送到错误的对话 ⭐⭐
- 用户可能发到了：
  - 另一个钉钉群
  - 另一个钉钉账号 (work-intel vs default)
  - 钉钉原生聊天而非机器人对话

### 原因 3：Gateway 重启期间消息丢失 ⭐
- 20:18:05 的 Gateway 重启可能导致短暂的消息窗口丢失
- Stream 重连期间钉钉推送可能超时

## 验证方法

### 1. 检查钉钉机器人配置
```bash
# 查看钉钉开放平台后台
# - 回调地址是否正确
# - 消息加密配置
# - 机器人是否在群内
```

### 2. 监控 Stream 心跳
```bash
# 添加 Stream 连接心跳监控
# 检测长时间无消息推送的情况
```

### 3. 启用详细日志
```json
// openclaw.json
"dingtalk": {
  "logLevel": "debug"
}
```

## 建议修复

### 短期方案
1. ✅ 增加 Stream 连接健康检查（不只是 WebSocket 状态）
2. ✅ 添加消息接收超时告警（如 10 分钟无消息）
3. ✅ Gateway 重启时记录更详细的状态

### 长期方案
1. 🔄 考虑切换到 Webhook 模式（更可靠）
2. 🔄 实现消息接收确认机制
3. 🔄 添加多账号消息路由诊断

## 已实施修复 (2026-03-14 20:48)

### 1. 消息接收监控脚本
- **文件**: `scripts/dingtalk-monitor-check.sh`
- **频率**: 每分钟检查一次
- **功能**: 检测超过 10 分钟无消息时记录告警
- **日志**: `/tmp/openclaw/dingtalk-monitor.log`
- **状态**: `/tmp/openclaw/dingtalk-monitor-state.json`

### 2. Crontab 配置
```bash
* * * * * /Users/ssd/.openclaw/workspace/scripts/dingtalk-monitor-check.sh
```

### 3. 告警冷却机制
- 首次告警后 30 分钟内不重复告警
- 避免日志刷屏

---

## 下一步行动

- [ ] 观察监控脚本运行情况（24 小时）
- [ ] 根据实际数据调整告警阈值
- [ ] 如问题持续，考虑切换到 Webhook 模式

---
调查时间：2026-03-14 20:29
更新时间：2026-03-14 20:48
