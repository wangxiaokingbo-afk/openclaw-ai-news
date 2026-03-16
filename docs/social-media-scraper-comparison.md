# 社交媒体爬虫能力对比

_最后更新：2026-03-15 01:30_

---

## 快速结论

| 平台 | 免登录爬取 | 热门内容 | 评论/点赞详情 | 状态 |
|------|-----------|---------|--------------|------|
| **YouTube** | ✅ 完全支持 | ✅ 趋势/热门视频 | ✅ 完整数据 | 🟢 就绪 |
| **TikTok** | ✅ 完全支持 | ✅ 发现页/ trending | ✅ 完整数据 | 🟢 就绪 |
| **X/Twitter** | ⚠️ 部分限制 | ⚠️ 需搜索 Actor | ⚠️ 基础数据 | 🟡 需配置 |
| **小红书** | ❌ 无官方 Actor | ❌ 不支持 | ❌ 不支持 | 🔴 需定制 |

---

## 各平台详细能力

### 📺 YouTube（最完善）

**可用 Actors**（5 个）：

| Actor ID | 免登录 | 热门内容 | 评论 | 点赞/播放 | 说明 |
|----------|--------|---------|------|----------|------|
| `streamers/youtube-scraper` | ✅ | ✅ 趋势榜 | ✅ | ✅ | 综合最佳 |
| `streamers/youtube-channel-scraper` | ✅ | - | - | ✅ | 频道数据 |
| `streamers/youtube-comments-scraper` | ✅ | - | ✅ | ✅ | 评论专用 |
| `streamers/youtube-shorts-scraper` | ✅ | ✅ Shorts 热门 | ✅ | ✅ | Shorts 专用 |
| `streamers/youtube-video-scraper-by-hashtag` | ✅ | ✅ 标签热门 | ✅ | ✅ | 标签搜索 |

**可获取数据**：
- ✓ 视频标题、描述、时长、上传日期
- ✓ 播放量、点赞数、评论数
- ✓ 评论列表（含回复、点赞）
- ✓ 频道订阅数、总播放量
- ✓ 趋势榜、标签热门

**限制**：
- 无法获取年龄限制视频
- 私有视频/评论不可见

---

### 🎵 TikTok（完善）

**可用 Actors**（14 个）：

| Actor ID | 免登录 | 热门内容 | 评论 | 点赞/播放 | 说明 |
|----------|--------|---------|------|----------|------|
| `clockworks/tiktok-scraper` | ✅ | ✅ 推荐页 | ✅ | ✅ | 综合最佳 |
| `clockworks/free-tiktok-scraper` | ✅ | ✅ | ✅ | ✅ | 免费版本 |
| `clockworks/tiktok-trends-scraper` | ✅ | ✅ 趋势榜 | ✅ | ✅ | 趋势专用 |
| `clockworks/tiktok-discover-scraper` | ✅ | ✅ 发现页 | ✅ | ✅ | 发现页 |
| `clockworks/tiktok-comments-scraper` | ✅ | - | ✅ | ✅ | 评论专用 |
| `clockworks/tiktok-hashtag-scraper` | ✅ | ✅ 标签热门 | ✅ | ✅ | 标签搜索 |

**可获取数据**：
- ✓ 视频描述、音乐、标签
- ✓ 播放量、点赞数、评论数、分享数
- ✓ 评论列表（含回复）
- ✓ 用户粉丝数、关注数
- ✓ 趋势标签、热门音乐

**限制**：
- 私有账号内容不可见
- 直播数据有限

---

### 🐦 X/Twitter（部分支持）

**状态**：技能文档未列出专用 Actor，需动态搜索

**搜索方法**：
```bash
mcpc --json mcp.apify.com \
  --header "Authorization: Bearer $APIFY_TOKEN" \
  tools-call search-actors \
  keywords:="twitter scraper" limit:=10
```

**已知限制**：
- ⚠️ X 平台 API 政策收紧，多数爬虫需要登录
- ⚠️ 免登录只能获取有限公开数据
- ⚠️ 评论/转发数据可能不完整

**替代方案**：
1. 使用 Apify 的 `twitter-scraper`（需 Cookie）
2. 使用 RSS 订阅（限公开账号）
3. 定制爬虫（需维护）

---

### 📕 小红书（不支持）

**状态**：❌ Apify Store 无官方 Actor

**原因**：
- 小红书反爬严格，需要登录 + 验证码
- 无成熟公开爬虫方案
- 数据主要在中国境内，海外服务难以访问

**替代方案**：
1. **定制开发**：需要逆向 APP 协议（高难度）
2. **第三方服务**：如飞瓜数据、新红等（付费）
3. **手动采集**：少量数据时可考虑

---

## 使用示例

### YouTube 热门视频爬取

**输入**：
```json
{
  "actor": "streamers/youtube-scraper",
  "input": {
    "searchMode": "trending",
    "region": "US",
    "maxResults": 50
  },
  "output": "2026-03-15_youtube_trending.csv"
}
```

**输出字段**：
```
videoId, title, channel, views, likes, comments, publishedAt, duration
```

---

### TikTok 趋势内容爬取

**输入**：
```json
{
  "actor": "clockworks/tiktok-trends-scraper",
  "input": {
    "region": "US",
    "count": 100
  },
  "output": "2026-03-15_tiktok_trends.json"
}
```

**输出字段**：
```
videoId, description, author, plays, likes, comments, shares, hashtags, music
```

---

## 配置要求

### 必需配置

```bash
# 1. 获取 Apify Token（注册免费账号）
# https://apify.com/account#/integrations

# 2. 配置到 OpenClaw
openclaw configure --set APIFY_TOKEN=你的_token
```

### 免费额度

| 项目 | 免费额度 | 说明 |
|------|---------|------|
| Apify 免费计划 | 5 美元/月 | 约 1000-5000 次爬取 |
| 计算单元 | 免费额度 | 简单爬虫消耗少 |
| 代理 | 免费共享 | 够用，可选付费独享 |

---

## 推荐工作流

### 场景 1：每日热门监控

```
1. YouTube 趋势榜 → 每日 9AM
2. TikTok 趋势榜 → 每日 9AM
3. 数据汇总 → CSV + 关键指标
4. 异常检测 → 播放量突增内容
```

### 场景 2：竞品分析

```
1. 指定频道/账号 → 爬取全部视频
2. 评论情感分析 → 提取关键词
3. 数据对比 → 播放/点赞/评论趋势
4. 报告生成 → 每周/每月
```

### 场景 3：标签监控

```
1. 指定标签 → 爬取热门内容
2. 创作者识别 → 头部账号
3. 内容分析 → 主题/风格
4. 机会发现 → 低竞争高流量标签
```

---

## 常见问题

**Q: 为什么小红书不支持？**
A: 小红书反爬严格，需要登录 + 手机验证，且服务器在国内，海外爬虫服务难以稳定访问。

**Q: X/Twitter 真的无法免登录爬取吗？**
A: 2023 年后 X 大幅限制未登录访问，多数爬虫需要 Cookie。建议用官方 API 或 RSS 替代。

**Q: 免费额度够用吗？**
A: 个人使用足够。YouTube/TikTok 简单爬取每次约 0.1-0.5 美元额度。

**Q: 数据更新频率？**
A: 实时爬取，但建议设置合理间隔（如每 10 分钟）避免被封。

---

## 下一步

1. **配置 APIFY_TOKEN**
2. **测试 YouTube/TikTok 爬取**
3. **评估 X/Twitter 替代方案**
4. **小红书考虑定制开发**

---

_文档基于 `apify-ultimate-scraper` v1.0.8 技能文档整理_
