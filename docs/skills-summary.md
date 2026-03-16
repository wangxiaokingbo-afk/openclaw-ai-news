# 🧰 新安装 Skills 使用指南

> 创建时间：2026-03-08  
> 共 8 个 skills

---

## 📋 总览

| Skill | 用途 | 难度 |
|-------|------|------|
| 🌐 openclaw-tavily-search | Tavily 网络搜索 | ⭐ |
| 🔍 find-skills | 发现新 skills | ⭐ |
| 🛡️ skill-vetting | 安全审查 skills | ⭐⭐ |
| 🧠 self-improving | 自我反思 + 记忆 | ⭐⭐⭐ |
| 🧾 summarize | 总结 URL/文件/视频 | ⭐ |
| ⚡ using-superpowers | 强制使用 skills | ⭐⭐ |
| 🐙 github | GitHub CLI 交互 | ⭐⭐ |
| 🌍 agent-browser | 浏览器自动化 | ⭐⭐⭐ |

---

## 1️⃣ 🌐 openclaw-tavily-search

**用途：** 使用 Tavily API 进行网络搜索（Brave Search 的替代方案）

### 🔑 配置
```bash
# 设置 API 密钥（二选一）
export TAVILY_API_KEY="your-key"
# 或写入 ~/.openclaw/.env
```

### 📖 典型用法

```bash
# 基础搜索
python3 skills/openclaw-tavily-search/scripts/tavily_search.py \
  --query "AI 助手最佳实践" --max-results 5

# 包含简短答案
python3 ... --query "..." --include-answer

# 输出为 Markdown 格式
python3 ... --query "..." --format md
```

### 💡 使用场景
- ✅ 搜索最新的技术文档
- ✅ 查找特定主题的参考资料
- ✅ 需要带摘要的搜索结果

---

## 2️⃣ 🔍 find-skills

**用途：** 发现和安装新的 agent skills

### 📖 典型用法

```bash
# 搜索技能
npx skills find react performance

# 安装技能
npx skills add vercel-labs/agent-skills@vercel-react-best-practices -g -y

# 检查更新
npx skills check

# 浏览技能网站
# https://skills.sh/
```

### 💡 使用场景
- ✅ 用户问"有没有 skill 可以做 X？"
- ✅ 需要扩展 agent 能力
- ✅ 查找特定领域的工具（测试、部署、文档等）

### 🎯 常见分类
| 类别 | 搜索关键词 |
|------|-----------|
| Web 开发 | react, nextjs, typescript, tailwind |
| 测试 | testing, jest, playwright, e2e |
| DevOps | deploy, docker, kubernetes, ci-cd |
| 代码质量 | review, lint, refactor, best-practices |

---

## 3️⃣ 🛡️ skill-vetting

**用途：** 安全审查 ClawHub skills（安装前必用！）

### 📖 审查流程

```bash
# 1. 下载到临时目录
cd /tmp
curl -L -o skill.zip "https://clawhub.ai/api/v1/download?slug=SKILL_NAME"
mkdir skill-inspect && cd skill-inspect
unzip -q ../skill.zip

# 2. 运行自动扫描器
python3 ~/.openclaw/workspace/skills/skill-vetting/scripts/scan.py .

# 3. 手动审查
cat SKILL.md
cat scripts/*.py

# 4. 检查 prompt injection
grep -rniE "ignore.*instruction|disregard.*previous" .
```

### ⚠️ 危险信号（立即拒绝）
- 🚫 `eval()`/`exec()` 无合理解释
- 🚫 base64 编码的字符串（非数据/图片）
- 🚫 访问未知域名或 IP
- 🚫 行为与文档不符
- 🚫 混淆代码

### 📊 决策矩阵
| 安全性 | 实用性 | 决定 |
|--------|--------|------|
| ✅ 干净 | 🔥 高 | **安装** |
| ✅ 干净 | ⚠️ 一般 | 考虑（先测试） |
| ⚠️ 问题 | 任意 | **调查** |
| 🚨 恶意 | 任意 | **拒绝** |

---

## 4️⃣ 🧠 self-improving

**用途：** 自我反思 + 自我批评 + 自我学习 + 记忆管理

### 📁 记忆结构
```
~/self-improving/
├── memory.md          # HOT: ≤100 行，始终加载
├── index.md           # 主题索引
├── projects/          # 项目特定学习
├── domains/           # 领域特定（代码、写作等）
├── archive/           # COLD: 归档内容
└── corrections.md     # 最近 50 条纠正记录
```

### 📖 典型用法

**自动记录纠正：**
```
用户说："不，应该是..."
用户说："我更喜欢 X，不是 Y"
用户说："记住我总是..."
→ 记录到 corrections.md
```

**自我反思格式：**
```
CONTEXT: [任务类型]
REFLECTION: [我发现的问题]
LESSON: [下次如何改进]
```

**查询命令：**
```bash
# 查看记忆统计
"memory stats"

# 查看最近纠正
"what have you learned?"

# 查看特定项目模式
"show [project] patterns"
```

### 💡 使用场景
- ✅ 用户纠正你时
- ✅ 完成重要工作后自我评估
- ✅ 发现可以改进的地方
- ✅ 需要长期记忆用户偏好

---

## 5️⃣ 🧾 summarize

**用途：** 快速总结 URL、本地文件、YouTube 视频

### 🔑 配置
```bash
# 安装 CLI
brew install steipete/tap/summarize

# 设置 API 密钥（根据选择的模型）
export GEMINI_API_KEY="..."  # Google
export OPENAI_API_KEY="..."  # OpenAI
export ANTHROPIC_API_KEY="..." # Anthropic
```

### 📖 典型用法

```bash
# 总结网页
summarize "https://example.com/article" \
  --model google/gemini-3-flash-preview

# 总结 PDF
summarize "/path/to/document.pdf" \
  --model google/gemini-3-flash-preview

# 总结 YouTube 视频
summarize "https://youtu.be/dQw4w9WgXcQ" --youtube auto

# 控制长度
summarize "https://..." --length short
summarize "https://..." --length long

# JSON 输出（机器可读）
summarize "https://..." --json
```

### 💡 使用场景
- ✅ 快速了解长文章要点
- ✅ 提取 PDF/文档摘要
- ✅ YouTube 视频内容总结
- ✅ 批量处理多个 URL

---

## 6️⃣ ⚡ using-superpowers

**用途：** 元技能 - 强制在任何任务前先检查并使用相关 skills

### 🚨 核心规则

```
⚠️ 如果有 1% 的可能性某个 skill 适用，你 ABSOLUTELY MUST 调用它！

这不是可选的，不能商量，不能找借口跳过。
```

### 📖 使用流程

```
1. 收到用户消息
         ↓
2. 是否有任何 skill 可能适用？（即使 1%）
         ↓ 是
3. 调用 Skill 工具
         ↓
4. 宣布："Using [skill] to [purpose]"
         ↓
5. 有检查清单？→ 创建 TodoWrite
         ↓
6. 严格按照 skill 执行
         ↓
7. 响应用户
```

### 🚩 危险信号（停止！你在找借口）
| 想法 | 现实 |
|------|------|
| "这只是个简单问题" | 问题也是任务，先检查 skills |
| "我需要先了解更多上下文" | 技能检查在澄清问题之前 |
| "我先快速查看代码" | skills 告诉你如何探索 |
| "这个 skill 太复杂了" | 简单事变复杂，正需要 skill |

### 💡 使用场景
- ✅ **每个对话开始时**
- ✅ 任何任务执行前
- ✅ 需要确保不遗漏可用技能时

---

## 7️⃣ 🐙 github

**用途：** 使用 `gh` CLI 与 GitHub 交互

### 🔑 配置
```bash
# 安装 gh CLI
brew install gh

# 认证
gh auth login
```

### 📖 典型用法

**Pull Requests：**
```bash
# 查看 PR 的 CI 状态
gh pr checks 55 --repo owner/repo

# 列出最近的 workflow runs
gh run list --repo owner/repo --limit 10

# 查看失败的步骤
gh run view <run-id> --repo owner/repo --log-failed
```

**Issues：**
```bash
# 列出 issues（JSON 过滤）
gh issue list --repo owner/repo \
  --json number,title \
  --jq '.[] | "\(.number): \(.title)"'
```

**高级 API 查询：**
```bash
# 获取 PR 特定字段
gh api repos/owner/repo/pulls/55 \
  --jq '.title, .state, .user.login'
```

### 💡 使用场景
- ✅ 检查 PR 的 CI 状态
- ✅ 查看 workflow 运行日志
- ✅ 批量查询 issues/PRs
- ✅ 自动化 GitHub 操作

---

## 8️⃣ 🌍 agent-browser

**用途：** 浏览器自动化（点击、填写、截图、数据提取）

### 🔑 配置
```bash
# 安装
npm install -g agent-browser
agent-browser install
agent-browser install --with-deps
```

### 📖 核心工作流

```bash
# 1. 打开页面
agent-browser open https://example.com

# 2. 获取可交互元素（带 refs）
agent-browser snapshot -i
# 输出：textbox "Email" [ref=e1], button "Submit" [ref=e2]

# 3. 使用 refs 交互
agent-browser fill @e1 "user@example.com"
agent-browser click @e2

# 4. 等待并检查结果
agent-browser wait --load networkidle
agent-browser snapshot -i
```

### 🎯 常用命令

**导航：**
```bash
agent-browser open <url>
agent-browser back / forward / reload
agent-browser close
```

**交互：**
```bash
agent-browser click @e1
agent-browser fill @e2 "text"
agent-browser press Enter
agent-browser hover @e1
agent-browser select @e1 "value"
```

**获取信息：**
```bash
agent-browser get text @e1
agent-browser get html @e1
agent-browser get url
agent-browser get count ".item"
```

**截图/PDF：**
```bash
agent-browser screenshot page.png
agent-browser screenshot --full    # 整页
agent-browser pdf output.pdf
```

**视频录制：**
```bash
agent-browser record start ./demo.webm
# ... 执行操作 ...
agent-browser record stop
```

### 💡 使用场景
- ✅ 自动化表单填写
- ✅ 网页数据提取
- ✅ UI 测试
- ✅ 截图/录屏演示
- ✅ 需要登录的网站操作

### ⚠️ 注意事项
- refs 在页面加载后稳定，导航后会变化
- 每次导航后重新 snapshot
- 使用 `fill` 而非 `type`（自动清空）

---

## 🎓 快速参考卡

### 🔰 新手推荐顺序
1. ⭐ **using-superpowers** - 确保始终使用可用技能
2. ⭐ **summarize** - 快速总结网页/文档
3. ⭐ **find-skills** - 发现更多技能
4. ⭐⭐ **github** - GitHub 工作流
5. ⭐⭐ **skill-vetting** - 安全审查
6. ⭐⭐⭐ **agent-browser** - 浏览器自动化
7. ⭐⭐⭐ **self-improving** - 长期记忆

### 📞 常用命令速查

```bash
# 搜索技能
npx skills find <query>

# 安装技能
clawhub install <skill-name>

# 总结网页
summarize "https://..." --length short

# GitHub PR 检查
gh pr checks <num> --repo owner/repo

# 浏览器自动化
agent-browser open <url>
agent-browser snapshot -i
agent-browser click @e1

# 记忆统计
"memory stats"
```

---

## 🔗 相关资源

- **ClawHub:** https://clawhub.com
- **Skills.sh:** https://skills.sh/
- **Summarize:** https://summarize.sh
- **Agent Browser:** https://github.com/vercel-labs/agent-browser

---

_文档由 小橙 🍊 创建_
