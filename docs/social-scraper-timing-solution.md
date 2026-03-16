# 社交媒体定时爬取方案

_最后更新：2026-03-15 01:45_

---

## 核心需求

- **平台**：小红书、X/Twitter、YouTube、TikTok
- **频率**：每 6 小时一次
- **数据**：热门内容、评论、点赞详情

---

## 工具对比

### 爬虫工具

| 工具 | 类型 | 小红书 | X/Twitter | YouTube | TikTok | 免登录 | 价格 |
|------|------|--------|-----------|---------|--------|--------|------|
| **TikHub API** | 社交媒体 API | ✅ | ✅ | ✅ | ✅ | ✅ | 按量 |
| **ScrapingBee** | 通用爬虫 | ❌ | ⚠️ | ⚠️ | ⚠️ | ❌ | $49+/月 |
| **Scrapinghub** | 通用爬虫 | ❌ | ⚠️ | ⚠️ | ⚠️ | ❌ | $49+/月 |
| **lxSpider** | 开源项目 | ✅ | ✅ | ⚠️ | ⚠️ | ❌ | 免费 |
| **Apify** | 爬虫平台 | ❌ | ⚠️ | ✅ | ✅ | ⚠️ | $5+/月 |

### 定时任务工具

| 工具 | 平台 | 精度 | 可靠性 | 推荐度 |
|------|------|------|--------|--------|
| **LaunchAgent** | macOS | 高 | ⭐⭐⭐⭐⭐ | 🟢 最佳 |
| **Crontab** | Unix | 高 | ⭐⭐⭐⭐ | 🟢 推荐 |
| **Windows 任务计划** | Windows | 高 | ⭐⭐⭐⭐ | 🟢 推荐 |
| **GitHub Actions** | 云端 | 中 | ⭐⭐⭐ | 🟡 备选 |
| **HEARTBEAT.md** | OpenClaw | 低 | ⭐⭐ | 🔴 不推荐 |

---

## 推荐方案

### 🏆 最佳组合：TikHub API + LaunchAgent

**架构**：
```
LaunchAgent (每 6 小时触发)
    ↓
Python 脚本 (调用 TikHub SDK)
    ↓
TikHub API (获取数据)
    ↓
保存 CSV/JSON + 钉钉通知
```

**优点**：
- ✅ 稳定可靠（macOS 原生服务）
- ✅ 免登录（无需维护 Cookie）
- ✅ 数据结构化（JSON 格式）
- ✅ 多平台支持

---

## 实现步骤

### 步骤 1：安装 TikHub SDK

```bash
pip install tikhub
```

### 步骤 2：配置 API Key

```bash
openclaw configure --set TIKHUB_API_KEY=你的_key
```

### 步骤 3：创建爬取脚本

```python
#!/usr/bin/env python3
# /Users/ssd/.openclaw/workspace/scripts/scrape_social.py

import asyncio
import json
from datetime import datetime
from tikhub import Client

async def main():
    # 初始化客户端
    client = Client(
        base_url="https://api.tikhub.io",
        api_key="YOUR_API_KEY",
        timeout=60
    )
    
    timestamp = datetime.now().strftime("%Y-%m-%d_%H%M")
    
    # 1. 爬取小红书热门笔记
    print(f"[{timestamp}] 爬取小红书...")
    xhs_data = await client.XiaohongshuWeb.fetch_trending_notes(limit=50)
    save_data(xhs_data, f"xiaohongshu_{timestamp}.json")
    
    # 2. 爬取 TikTok 热门
    print(f"[{timestamp}] 爬取 TikTok...")
    tiktok_data = await client.TikTokWeb.fetch_trending_videos(limit=50)
    save_data(tiktok_data, f"tiktok_{timestamp}.json")
    
    # 3. 爬取 YouTube 热门
    print(f"[{timestamp}] 爬取 YouTube...")
    yt_data = await client.YouTubeWeb.fetch_trending_videos(limit=50)
    save_data(yt_data, f"youtube_{timestamp}.json")
    
    # 4. 爬取 X/Twitter 热门
    print(f"[{timestamp}] 爬取 X/Twitter...")
    twitter_data = await client.TwitterWeb.fetch_trending_topics()
    save_data(twitter_data, f"twitter_{timestamp}.json")
    
    print(f"[{timestamp}] 完成！")

def save_data(data, filename):
    """保存数据到 JSON 文件"""
    path = f"/Users/ssd/.openclaw/workspace/data/{filename}"
    with open(path, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    print(f"  → 保存到 {path}")

if __name__ == "__main__":
    asyncio.run(main())
```

### 步骤 4：创建 LaunchAgent

```xml
<!-- ~/Library/LaunchAgents/social-scraper.plist -->
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" 
  "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
    <key>Label</key>
    <string>com.social.scraper</string>
    
    <key>ProgramArguments</key>
    <array>
        <string>/usr/bin/python3</string>
        <string>/Users/ssd/.openclaw/workspace/scripts/scrape_social.py</string>
    </array>
    
    <key>WorkingDirectory</key>
    <string>/Users/ssd/.openclaw/workspace</string>
    
    <key>StandardOutPath</key>
    <string>/tmp/social-scraper-stdout.log</string>
    
    <key>StandardErrorPath</key>
    <string>/tmp/social-scraper-stderr.log</string>
    
    <key>StartInterval</key>
    <integer>21600</integer>  <!-- 6 小时 = 21600 秒 -->
    
    <key>RunAtLoad</key>
    <true/>
</dict>
</plist>
```

加载服务：
```bash
launchctl load ~/Library/LaunchAgents/social-scraper.plist
```

### 步骤 5：验证

```bash
# 查看服务状态
launchctl list | grep social-scraper

# 手动运行测试
python3 /Users/ssd/.openclaw/workspace/scripts/scrape_social.py

# 查看日志
tail -20 /tmp/social-scraper-stdout.log
```

---

## 数据输出示例

### 目录结构

```
/Users/ssd/.openclaw/workspace/data/
├── xiaohongshu_2026-03-15_0600.json
├── tiktok_2026-03-15_0600.json
├── youtube_2026-03-15_0600.json
├── twitter_2026-03-15_0600.json
├── xiaohongshu_2026-03-15_1200.json
└── ...
```

### 数据格式（小红书示例）

```json
{
  "timestamp": "2026-03-15T06:00:00+08:00",
  "platform": "xiaohongshu",
  "notes": [
    {
      "note_id": "65f1a2b3c4d5e6f7",
      "title": "标题",
      "author": {
        "user_id": "123456",
        "nickname": "作者名",
        "avatar": "https://..."
      },
      "content": "正文内容...",
      "like_count": 1234,
      "collect_count": 567,
      "comment_count": 89,
      "share_count": 12,
      "tags": ["标签 1", "标签 2"],
      "images": ["url1", "url2"],
      "video_url": "https://...",
      "publish_time": "2026-03-14T10:00:00+08:00",
      "ip_region": "上海"
    }
  ]
}
```

---

## 成本估算

### TikHub API 调用量

| 平台 | 每次调用 | 每日 4 次 | 每月调用 | 估算成本 |
|------|---------|---------|---------|---------|
| 小红书 | 50 笔记 | 200 次 | 6,000 次 | ~$6-$60 |
| TikTok | 50 视频 | 200 次 | 6,000 次 | ~$6-$60 |
| YouTube | 50 视频 | 200 次 | 6,000 次 | ~$6-$60 |
| X/Twitter | 50 推文 | 200 次 | 6,000 次 | ~$6-$60 |
| **合计** | - | **800 次/日** | **24,000 次/月** | **~$24-$240/月** |

**注**：实际价格需登录 TikHub 后台查询，以上为估算。

---

## 扩展功能

### 1. 钉钉通知

```python
import requests

def send_dingtalk_alert(message):
    """发送钉钉通知"""
    webhook = "YOUR_DINGTALK_WEBHOOK"
    data = {
        "msgtype": "text",
        "text": {
            "content": f"📊 社交媒体爬取完成\n{message}"
        }
    }
    requests.post(webhook, json=data)
```

### 2. 数据汇总报告

```python
def generate_daily_report():
    """生成每日汇总报告"""
    # 读取当日所有数据
    # 统计各平台热门内容
    # 生成 HTML/PDF 报告
    pass
```

### 3. 异常重试

```python
from tenacity import retry, stop_after_attempt, wait_exponential

@retry(stop=stop_after_attempt(3), wait=wait_exponential())
async def fetch_with_retry(client, endpoint, **kwargs):
    """带重试的 API 调用"""
    return await endpoint(**kwargs)
```

---

## 常见问题

**Q: 为什么不用 ScrapingBee？**
A: ScrapingBee 是通用网页爬虫，对社交媒体支持有限，需要自己处理登录、Cookie、反爬等。TikHub 专门针对社交媒体，开箱即用。

**Q: 6 小时频率会不会太高？**
A: 不会。TikHub API 限制约 5 次/秒，每次爬取 4 个平台约 4 次调用，6 小时一次远低于限制。

**Q: 数据能保存多久？**
A: 本地存储，永久保存。建议定期归档（如每月打包）。

**Q: 可以实时爬取吗？**
A: 可以，但建议考虑：
- API 成本会增加
- 数据冗余可能较高
- 推荐 1-6 小时间隔

---

## 下一步

1. **注册 TikHub**：https://beta-web.tikhub.io
2. **获取 API Key**
3. **测试 API**：确认数据质量
4. **部署脚本**：配置 LaunchAgent
5. **验证运行**：检查首次执行

---

_需要我帮你创建完整的爬取脚本和配置吗？_
