# 钉钉连接稳定性解决方案

## 问题根因

**REGISTERED 标志不可靠** - 这是钉钉 Stream SDK 的已知行为：

```typescript
// 来自 ~/.openclaw/extensions/dingtalk/src/monitor.ts 源码注释:
// "REGISTERED flag may not always be set by DingTalk server after reconnects,
//  but CALLBACK messages can still arrive."
```

### 之前的错误逻辑

旧版保活脚本将 `REGISTERED not set` 视为故障，导致：
- ✗ 连接实际正常但被误判为异常
- ✗ 频繁重启 Gateway，反而打断正常连接
- ✗ 日志中持续出现 "REGISTERED not set" 是正常现象

### 正确的健康判断标准

| 状态 | 含义 | 是否需要处理 |
|------|------|-------------|
| `Stream client connected` | WebSocket 已建立 | ✓ 正常 |
| `reconnect succeeded` | 重连成功 | ✓ 正常 |
| `WebSocket open, REGISTERED not set` | 连接正常，标志未设置 | ✓ **正常（忽略）** |
| `connection lost` | 连接断开 | ⚠ 需要关注 |
| `abnormal closure` | 异常关闭 | ⚠ 需要关注 |

---

## 已实施的修复

### 1. 更新保活脚本 (`dingtalk-keepalive.sh v4`)

**变更内容：**
- ✗ 移除：不再检测 `REGISTERED not set`
- ✓ 新增：检测实际连接故障（`connection lost`、`abnormal closure`）
- ✓ 新增：只有连续 5 次故障才触发重启

### 2. 更新 crontab 配置

```bash
# 每 10 分钟探活检查
*/10 * * * * /Users/ssd/.openclaw/workspace/scripts/dingtalk-keepalive.sh

# 每 3 小时定时刷新（预防性重启）
0 */3 * * * /Users/ssd/.openclaw/workspace/scripts/dingtalk-refresh.sh

# 每天凌晨 3 点诊断报告
0 3 * * * /Users/ssd/.openclaw/workspace/scripts/dingtalk-diagnose.sh >> /tmp/openclaw/dingtalk-diagnose.log 2>&1
```

### 3. 新增诊断工具

运行诊断脚本快速检查状态：
```bash
~/.openclaw/workspace/scripts/dingtalk-diagnose.sh
```

---

## 验证方法

### 立即验证

```bash
# 1. 运行诊断
~/.openclaw/workspace/scripts/dingtalk-diagnose.sh

# 2. 检查 Gateway 状态
openclaw gateway status

# 3. 查看最新保活日志
tail -10 /tmp/openclaw/dingtalk-keepalive.log
```

### 预期结果

- ✓ Gateway 状态：`Runtime: running`, `RPC probe: ok`
- ✓ 连接日志：有 `Stream client connected` 或 `WebSocket open`
- ✓ 保活日志：显示 `✓ Connection healthy (REGISTERED flag ignored)`

---

## 后续监控

### 保活日志位置
```
/tmp/openclaw/dingtalk-keepalive.log
```

### 诊断日志位置
```
/tmp/openclaw/dingtalk-diagnose.log  # 每日凌晨 3 点生成
```

### 何时需要手动干预

| 现象 | 可能原因 | 操作 |
|------|---------|------|
| 连续出现 `connection lost` | 网络问题或钉钉服务器问题 | 运行诊断脚本，检查网络 |
| Gateway 无法启动 | 配置错误或端口冲突 | `openclaw gateway restart` |
| 消息无法收发 | 机器人配置过期 | 检查钉钉开放平台机器人状态 |

---

## 关于 HEARTBEAT.md 的说明

**重要：** `HEARTBEAT.md` 中的配置只是文档注释，**不会自动执行**。

OpenClaw 的 heartbeat 机制需要主会话收到心跳 poll 消息才会触发，不是后台定时任务。

**正确的定时任务方案：**
1. ✓ 使用系统 crontab（已配置）
2. ✓ 使用独立脚本（已提供）
3. ✗ 不要依赖 HEARTBEAT.md 自动执行

---

## 相关文件

| 文件 | 用途 |
|------|------|
| `scripts/dingtalk-keepalive.sh` | 保活探活脚本（v4 已修复） |
| `scripts/dingtalk-refresh.sh` | 定时刷新脚本 |
| `scripts/dingtalk-diagnose.sh` | 诊断工具 |
| `scripts/dingtalk-crontab.txt` | crontab 配置备份 |
| `/tmp/openclaw/dingtalk-keepalive.log` | 保活日志 |
| `/tmp/openclaw/openclaw-YYYY-MM-DD.log` | Gateway 日志 |

---

_最后更新：2026-03-13_
