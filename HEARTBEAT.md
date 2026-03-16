# HEARTBEAT.md

# Keep this file empty (or with only comments) to skip heartbeat API calls.

# Add tasks below when you want the agent to check something periodically.

---
## ⚠️ 重要说明

**HEARTBEAT.md 不会自动执行定时任务！**

OpenClaw 的 heartbeat 机制需要主会话收到心跳 poll 消息才会触发，不是后台自动执行。

**定时任务请使用系统 crontab：**
- 钉钉保活：`crontab -l | grep dingtalk`
- 配置位置：`~/.openclaw/workspace/scripts/dingtalk-crontab.txt`
- 详见：`docs/dingtalk-stability-fix.md`

---
## 可用的 heartbeat 检查项（需手动触发）

- [ ] 检查未读邮件
- [ ] 检查日历事件（24-48h 内）
- [ ] 检查钉钉连接状态（运行诊断脚本）
