# Skills 使用指南表格

> 更新时间：2026-03-08  
> 总数：8 个 skills

---

## 📊 Skills 总览

| 序号 | Skill | 图标 | 用途 | 难度 | 配置要求 | 典型命令 |
|:---:|:-----|:---:|:-----|:---:|:---------|:---------|
| 1 | openclaw-tavily-search | 🌐 | Tavily 网络搜索 | ⭐ | TAVILY_API_KEY | `python3 tavily_search.py --query "..."` |
| 2 | find-skills | 🔍 | 发现新 skills | ⭐ | 无 | `npx skills find <query>` |
| 3 | skill-vetting | 🛡️ | 安全审查 skills | ⭐⭐ | Python 3 | `python3 scan.py .` |
| 4 | self-improving | 🧠 | 自我反思 + 记忆 | ⭐⭐⭐ | 初始化目录 | 自动触发 |
| 5 | summarize | 🧾 | 总结 URL/文件/视频 | ⭐ | 各模型 API Key | `summarize "url" --length short` |
| 6 | using-superpowers | ⚡ | 强制使用 skills | ⭐⭐ | 无 | 自动触发 |
| 7 | github | 🐙 | GitHub CLI 交互 | ⭐⭐ | gh CLI + 认证 | `gh pr checks <num>` |
| 8 | agent-browser | 🌍 | 浏览器自动化 | ⭐⭐⭐ | Node.js + npm | `agent-browser open <url>` |

---

## 🎯 使用场景对照表

| 需求 | 推荐 Skill | 命令示例 |
|------|-----------|---------|
| 搜索最新资料 | 🌐 tavily-search | `--query "AI 最佳实践" --max-results 5` |
| 找新技能扩展 | 🔍 find-skills | `npx skills find react testing` |
| 安装前安全检查 | 🛡️ skill-vetting | `curl -L -o skill.zip && unzip && scan.py .` |
| 记住用户偏好 | 🧠 self-improving | 自动记录纠正 → 存入 memory.md |
| 快速读长文章 | 🧾 summarize | `summarize "https://..." --length short` |
| 确保不漏技能 | ⚡ using-superpowers | 自动触发（1% 可能就要用） |
| 查 PR/CI 状态 | 🐙 github | `gh pr checks 55 --repo owner/repo` |
| 网页自动化 | 🌍 agent-browser | `open` → `snapshot -i` → `click @e1` |

---

## ⚠️ 注意事项

| Skill | 注意事项 |
|-------|---------|
| 🌐 tavily-search | 需要 API Key，保持 max-results ≤ 5 |
| 🛡️ skill-vetting | **安装前必用**，发现 eval/base64/未知域名→拒绝 |
| 🧠 self-improving | 记忆分 HOT/WARM/COLD 三层，定期整理 |
| 🧾 summarize | 支持 PDF/YouTube，需设置对应模型 API Key |
| ⚡ using-superpowers | **不可跳过**，即使觉得"很简单"也要检查 |
| 🐙 github | 需先 `gh auth login` 认证 |
| 🌍 agent-browser | refs 导航后变化，每次重新 snapshot |

---

## 📈 学习优先级

| 阶段 | Skills | 预计掌握时间 |
|------|--------|-------------|
| 新手入门 | ⭐ using-superpowers, ⭐ summarize, ⭐ find-skills | 1-2 天 |
| 进阶使用 | ⭐⭐ github, ⭐⭐ skill-vetting, ⭐ tavily-search | 3-5 天 |
| 高级应用 | ⭐⭐⭐ agent-browser, ⭐⭐⭐ self-improving | 1-2 周 |

---

## 🔗 相关资源

| 资源 | 链接 |
|------|------|
| ClawHub | https://clawhub.com |
| Skills.sh | https://skills.sh/ |
| Summarize | https://summarize.sh |
| Agent Browser | https://github.com/vercel-labs/agent-browser |
| 完整文档 | `/Users/ssd/.openclaw/workspace/docs/skills-summary.md` |

---

_由 小橙 🍊 整理_
