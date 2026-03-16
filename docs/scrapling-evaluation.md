# Scrapling 评估报告

_最后更新：2026-03-15 02:00_

---

## 项目信息

| 项目 | 值 |
|------|------|
| **名称** | Scrapling |
| **GitHub** | https://github.com/D4Vinci/Scrapling |
| **Stars** | 29,556 ⭐ |
| **Forks** | 2,238 |
| **语言** | Python 3.10+ |
| **许可证** | BSD-3 |
| **文档** | https://scrapling.readthedocs.io |
| **Discord** | https://discord.gg/EMgGbDceNQ |

---

## 核心特性

### 1. 自适应爬虫（Adaptive Scraping）

**痛点**：网站改版后爬虫失效，需要重新写选择器

**Scrapling 方案**：
```python
# 第一次爬取，自动保存选择器
products = page.css('.product', auto_save=True)

# 网站改版后，自动定位相似元素
products = page.css('.product', adaptive=True)
```

**原理**：
- 智能相似度算法
- 多特征匹配（文本、位置、属性）
- 自动 fallback 机制

---

### 2. 反反爬虫（Anti-Bot Bypass）

**支持的反爬系统**：
- ✅ Cloudflare Turnstile / Challenge
- ✅ Akamai Bot Manager
- ✅ DataDome
- ✅ 其他指纹检测

**使用方式**：
```python
from scrapling.fetchers import StealthyFetcher

# 自动绕过反爬
page = StealthyFetcher.fetch('https://target.com', headless=True)
```

**原理**：
- 浏览器指纹伪造
- TLS 指纹模拟
- 行为模式模仿

---

### 3. 完整爬虫框架（Spider Framework）

**类似 Scrapy，但更现代**：

```python
from scrapling.spiders import Spider, Response

class MySpider(Spider):
    name = "demo"
    start_urls = ["https://example.com/"]
    
    async def parse(self, response: Response):
        for item in response.css('.item'):
            yield {"title": item.css('::text').get()}

MySpider().start()
```

**特性**：
- ✅ 异步支持（async/await）
- ✅ 并发控制
- ✅ 请求去重
- ✅ 自动重试
- ✅ 导出支持（JSON/JSONL/CSV）

---

### 4. 断点续爬（Pause & Resume）

**场景**：长时间爬虫，中途被打断

**使用方式**：
```python
# 启动时自动检查检查点
spider = MySpider()
spider.start(resume=True)  # 从上次中断处继续
```

**原理**：
- 定期保存检查点
- 记录已请求 URL
- 保存待处理队列

---

### 5. 流式输出（Streaming Mode）

**场景**：需要实时看到爬取结果

**使用方式**：
```python
async for item in spider.stream():
    print(f"新数据：{item}")
    # 可实时存入数据库或推送
```

**优势**：
- 无需等待爬完
- 适合长任务
- 可对接 UI/管道

---

### 6. MCP 服务器（AI 集成）

**场景**：让 AI 直接调用爬虫

**安装**：
```bash
pip install "scrapling[ai]"
```

**使用**：
```python
# AI 发送指令，Scrapling 执行爬取
# 返回结构化数据，减少 token 消耗
```

**演示视频**：https://www.youtube.com/watch?v=qyFk3ZNwOxE

---

## 安装方式

### 方案 A：pip 安装

```bash
# 基础安装（仅解析器）
pip install scrapling

# 完整安装（含浏览器）
pip install "scrapling[all]"
scrapling install

# 强制重装
scrapling install --force
```

### 方案 B：Docker（推荐）

```bash
# DockerHub
docker pull pyd4vinci/scrapling

# GitHub Registry
docker pull ghcr.io/d4vinci/scrapling:latest

# 运行
docker run --rm pyd4vinci/scrapling scrapling fetch https://example.com
```

---

## 针对你的场景

### 场景 1：小红书 POI 提取

```python
from scrapling.fetchers import StealthyFetcher

fetcher = StealthyFetcher(adaptive=True)

# 搜索页面
page = fetcher.fetch('https://www.xiaohongshu.com/search?keyword=三亚打卡')

# 自适应提取（网站改版也能用）
notes = page.css('.note-item, .search-result-item', adaptive=True)

for note in notes:
    poi = {
        'title': note.css('.title::text').get(),
        'author': note.css('.nickname::text').get(),
        'likes': note.css('.like-count::text').get(),
        'location': note.css('.location::text').get()
    }
    print(poi)
```

---

### 场景 2：X/Twitter 热门地点

```python
from scrapling.fetchers import StealthyFetcher

# 绕过登录墙
fetcher = StealthyFetcher()
page = fetcher.fetch('https://twitter.com/search?q=travel%20spot')

# 提取推文中的地点
tweets = page.css('[data-testid="tweet"]')
for tweet in tweets:
    text = tweet.css('[data-testid="tweetText"]::text').get()
    # 用 POI 提取技能从文本中提取地点
```

---

### 场景 3：YouTube 旅行攻略

```python
from scrapling.fetchers import DynamicFetcher

# YouTube 是动态加载，用 DynamicFetcher
fetcher = DynamicFetcher()
page = fetcher.fetch('https://www.youtube.com/results?search_query=travel+guide')

# 等待视频加载
page.wait_for_selector('#video-title')

videos = page.css('#video-title')
for video in videos:
    title = video.css('#video-title::attr(title)').get()
    url = video.css('#video-title::attr(href)').get()
```

---

### 场景 4：TikTok 网红打卡点

```python
from scrapling.fetchers import StealthyFetcher

# TikTok 反爬严格，用 StealthyFetcher + 代理
fetcher = StealthyFetcher(proxy="rotating")

page = fetcher.fetch('https://www.tiktok.com/search?q=travel%20spot')

videos = page.css('.video-item', adaptive=True)
for video in videos:
    data = {
        'desc': video.css('.video-desc::text').get(),
        'author': video.css('.author-name::text').get(),
        'likes': video.css('.like-count::text').get()
    }
```

---

## 定时任务集成

### 方案 A：LaunchAgent（macOS）

```xml
<!-- ~/Library/LaunchAgents/social-poi-scraper.plist -->
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" 
  "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
    <key>Label</key>
    <string>com.social.poi.scraper</string>
    
    <key>ProgramArguments</key>
    <array>
        <string>/usr/bin/python3</string>
        <string>/Users/ssd/.openclaw/workspace/scripts/social-poi-scraper.py</string>
    </array>
    
    <key>WorkingDirectory</key>
    <string>/Users/ssd/.openclaw/workspace</string>
    
    <key>StartInterval</key>
    <integer>21600</integer>  <!-- 6 小时 -->
    
    <key>RunAtLoad</key>
    <true/>
</dict>
</plist>
```

加载：
```bash
launchctl load ~/Library/LaunchAgents/social-poi-scraper.plist
```

---

### 方案 B：Crontab

```bash
# crontab -e
0 */6 * * * cd /Users/ssd/.openclaw/workspace && \
    python3 scripts/social-poi-scraper.py >> /tmp/poi-scraper.log 2>&1
```

---

## 成本对比

| 方案 | 成本 | 说明 |
|------|------|------|
| **Scrapling** | 免费 | 开源，自己部署 |
| **TikHub API** | $24-$240/月 | 按调用量 |
| **ScrapingBee** | $49-$599/月 | 订阅制 |
| **高德 API** | 免费 | 5000 次/日 |

---

## 优缺点总结

### ✅ 优点

| 优势 | 价值 |
|------|------|
| **自适应** | 网站改版不用改代码 |
| **反反爬** | 绕过 Cloudflare 等 |
| **框架完整** | 从单页到全站爬取 |
| **断点续爬** | 长任务不担心中断 |
| **流式输出** | 实时看到进度 |
| **AI 集成** | MCP 服务器对接 AI |
| **开源免费** | 无额外成本 |

### ⚠️ 缺点

| 劣势 | 说明 |
|------|------|
| **需自己写逻辑** | 不像 API 那样开箱即用 |
| **学习成本** | 需要理解爬虫概念 |
| **维护成本** | 需自己处理异常、反爬升级 |

---

## 推荐架构

### 最佳组合

```
┌─────────────────────┐
│    Scrapling 爬虫    │ ← 从社交媒体爬取 POI
│  (自适应 + 反反爬)   │
└──────────┬──────────┘
           │
           ▼
┌─────────────────────┐
│  POI 文本提取技能    │ ← 从文本提取地点名称
│    (已有)           │
└──────────┬──────────┘
           │
           ▼
┌─────────────────────┐
│   TikHub API        │ ← 补全经纬度、电话等
│   (按需调用)        │
└──────────┬──────────┘
           │
           ▼
┌─────────────────────┐
│   结构化输出        │
│ (JSON/CSV/数据库)   │
└─────────────────────┘
```

---

## 下一步

### 立即可做

1. **安装 Scrapling**：
   ```bash
   pip install "scrapling[all]"
   scrapling install
   ```

2. **测试小红书爬取**：
   ```python
   from scrapling.fetchers import StealthyFetcher
   page = StealthyFetcher.fetch('https://www.xiaohongshu.com/search?keyword=三亚')
   print(page.css('.note-item::text').get_all())
   ```

3. **创建定时任务**：
   - 配置 LaunchAgent 或 Crontab
   - 每 6 小时自动执行

### 优化方向

1. **扩展地名库**：在 POI 提取技能中添加更多地名
2. **代理轮换**：配置 Scrapling 的 ProxyRotator
3. **数据融合**：结合 Scrapling + TikHub API
4. **AI 集成**：配置 MCP 服务器，让 AI 直接调用

---

## 相关资源

| 资源 | 链接 |
|------|------|
| GitHub | https://github.com/D4Vinci/Scrapling |
| 文档 | https://scrapling.readthedocs.io |
| Docker | https://hub.docker.com/r/pyd4vinci/scrapling |
| Discord | https://discord.gg/EMgGbDceNQ |
| 赞助 | https://github.com/sponsors/D4Vinci |

---

_需要我帮你创建 Scrapling 爬虫脚本吗？_
