# 🔍 热点资讯推送 - 自我检查清单

**每次执行前必须逐项检查，全部确认后才能开始抓取！**

---

## ✅ 第一阶段：数据源检查 (必须 100% 符合)

### 数据源权重检查
- [ ] **X 平台 40%**：使用 `browser` 工具，`profile="chrome"`，@wang9067 登录态
  - [ ] 搜索关键词：AI、人工智能、新能源、地缘政治、金融、投资
  - [ ] ❌ 不搜索 Tesla
  - [ ] 排序：top + latest 综合
  - [ ] 热度公式：score = like×1 + repost×2 + reply×3 + view×0.001
  - [ ] 时间范围：最近 3-7 天

- [ ] **News Minimalist 30%**：使用 `browser` 访问 `https://www.newsminimalist.com`
  - [ ] significance 阈值：≥ 5.2
  - [ ] 追踪原媒体链接，阅读理解后提炼

- [ ] **Google 搜索 20%**：使用 `web_search` 工具
  - [ ] 搜索词：AI news、new energy、geopolitics、finance

- [ ] **YouTube 10%**：使用 `browser` 访问 YouTube 首页 trending
  - [ ] 只抓播客 (Podcasts) + 新闻 (News)
  - [ ] ❌ 不抓个人频道
  - [ ] 频道订阅数 > 10 万

### 禁止项检查
- [ ] ❌ 没有使用 The Verge
- [ ] ❌ 没有抓取个人 YouTube 频道
- [ ] ❌ X 平台没有搜索 Tesla
- [ ] ❌ 没有使用 SKILL.md 未授权的其他网站

---

## ✅ 第二阶段：内容规范检查

### 领域分布检查
- [ ] AI 50% = 5 条
- [ ] 新能源 30% = 3 条
- [ ] 商业金融 10% = 1 条
- [ ] 社会政治 10% = 1 条
- [ ] **总计 10 条**

### 内容质量检查
- [ ] AI 内容排除学习/教程类
- [ ] 每条资讯包含：标题 + 要点 + 锐评
- [ ] 锐评有独立观点和判断（不是简单复述）
- [ ] 锐评数量 = 10 条（每条资讯都有）

### 格式检查
- [ ] ❌ 没有生成"核心结论"部分（已永久删除）
- [ ] 报告从"资讯详情"直接开始
- [ ] 完整报告链接置底

---

## ✅ 第三阶段：输出检查

### 文件生成检查
- [ ] Markdown 报告：`daily-top10-YYYY-MM-DD-HHMM.md`
- [ ] HTML 报告：`daily-top10-YYYY-MM-DD-HHMM.html`
- [ ] 版本化命名（不覆盖历史文件）

### 部署检查
- [ ] git add 报告文件
- [ ] git commit（包含时间戳和锐评数量）
- [ ] git push origin main
- [ ] 更新 `config/pushed-items.json`

### 推送检查
- [ ] 发送钉钉 ActionCard 到 `cidwdUjqhs0Pc+p2nKu4pHyVQ==`
- [ ] 消息格式正确（10 条详情，链接置底）

---

## ✅ 第四阶段：平台状态检查

### 异常监控
- [ ] 检查 X 平台 Cookie 是否过期
- [ ] 检查 News Minimalist 可访问性
- [ ] 检查 YouTube 可访问性
- [ ] 检查 GitHub Pages 部署状态

### 异常处理
- [ ] 如有异常，在报告中红色警告
- [ ] 不跳过、不替换为未授权网站
- [ ] 降级方案：X→Google，News Minimalist→Google 搜索

---

## 🚨 执行前确认

**在开始抓取前，必须回答以下问题：**

1. **我准备使用哪些数据源？**
   - 答案必须是：X 平台、News Minimalist、Google 搜索、YouTube
   - 任何其他网站都是错误的！

2. **我是否使用了禁止的网站？**
   - The Verge？❌
   - 个人 YouTube 频道？❌
   - Tesla 相关搜索？❌

3. **如果平台异常，我会怎么做？**
   - 在报告中红色警告
   - 使用降级数据源（Google 搜索）
   - 不随意替换为未授权网站

4. **报告格式是否正确？**
   - 10 条资讯，每条有锐评
   - 没有核心结论部分
   - 领域分布 50/30/10/10

---

## 📝 执行日志模板

```
【自我检查完成】时间：YYYY-MM-DD HH:MM

✅ 数据源检查：通过
- X 平台：准备使用 chrome profile (@wang9067)
- News Minimalist：准备访问 https://www.newsminimalist.com
- Google 搜索：准备使用 web_search
- YouTube：准备抓取 trending 播客/新闻

✅ 禁止项检查：通过
- 未使用 The Verge
- 未使用未授权网站

✅ 内容规范：确认
- 领域分布：50/30/10/10
- 锐评数量：10 条
- 无核心结论部分

✅ 平台状态：
- X 平台：正常/异常（如异常将降级）
- News Minimalist：正常/异常（如异常将降级）
- YouTube：正常/异常

开始执行抓取...
```

---

**⚠️ 违反此检查清单的后果：**
- 报告质量不达标
- 违反用户明确禁止项
- 浪费执行时间和资源

**✅ 遵守此检查清单的好处：**
- 保证内容质量和一致性
- 尊重用户偏好和禁止项
- 建立可信赖的自动化流程

---

*最后更新：2026-03-18 (添加重大错误反思)*
