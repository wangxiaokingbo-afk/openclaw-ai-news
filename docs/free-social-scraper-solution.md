# 零成本社交媒体数据获取方案

_最后更新：2026-03-15 02:05_

---

## 核心架构

```
┌─────────────────────────────────────────────────────┐
│                  Scrapling 爬虫                      │
│  (免费开源，自适应，反反爬)                           │
└─────────────────┬───────────────────────────────────┘
                  │
    ┌─────────────┼─────────────┐
    ▼             ▼             ▼
┌────────┐   ┌────────┐   ┌────────┐
│小红书   │   │X/Twitter│  │YouTube │
│爬取    │   │爬取     │   │爬取    │
└────────┘   └────────┘   └────────┘
    │             │             │
    └─────────────┼─────────────┘
                  │
                  ▼
    ┌─────────────────────────┐
    │   POI 提取技能 (已有)    │
    │   - 地名识别             │
    │   - POI 类型分类         │
    │   - 置信度评分           │
    └───────────┬─────────────┘
                │
                ▼
    ┌─────────────────────────┐
    │   免费 API 补全 (可选)   │
    │   - 高德地图 (5000 次/日) │
    │   - OpenStreetMap (无限) │
    └───────────┬─────────────┘
                │
                ▼
    ┌─────────────────────────┐
    │   本地存储              │
    │   JSON/CSV/SQLite       │
    └─────────────────────────┘
```

---

## 零成本工具栈

| 组件 | 工具 | 成本 |
|------|------|------|
| **爬虫框架** | Scrapling | ✅ 免费开源 |
| **POI 提取** | 已有技能 | ✅ 免费 |
| **地图 API** | 高德地图 | ✅ 5000 次/日免费 |
| **地图 API** | OpenStreetMap | ✅ 完全免费 |
| **定时任务** | LaunchAgent/Crontab | ✅ 系统自带 |
| **数据存储** | JSON/SQLite | ✅ 本地存储 |

---

## 各平台爬取方案

### 1. 小红书

**挑战**：登录墙、反爬严格

**Scrapling 方案**：
```python
from scrapling.fetchers import StealthyFetcher

fetcher = StealthyFetcher(
    adaptive=True,  # 自适应
    headless=True,  # 无头模式
)

# 搜索页面（无需登录）
url = 'https://www.xiaohongshu.com/search_result?keyword=三亚旅行'
page = fetcher.fetch(url)

# 提取笔记
notes = page.css('.note-item, .search-result-item', adaptive=True)

for note in notes:
    data = {
        'title': note.css('.title::text').get(),
        'author': note.css('.nickname::text').get(),
        'likes': note.css('.like-count::text').get(),
        'content': note.css('.desc::text').get(),
        'url': note.css('a::attr(href)').get()
    }
    print(data)
```

**技巧**：
- ✅ 用搜索页面，无需登录
- ✅ StealthyFetcher 绕过反爬
- ✅ 自适应选择器，网站改版也能用

---

### 2. X/Twitter

**挑战**：登录墙、反爬

**Scrapling 方案**：
```python
from scrapling.fetchers import StealthyFetcher

fetcher = StealthyFetcher(adaptive=True)

# 搜索页面（部分公开）
url = 'https://twitter.com/search?q=travel%20spot&f=live'
page = fetcher.fetch(url)

# 提取推文
tweets = page.css('[data-testid="tweet"]', adaptive=True)

for tweet in tweets:
    data = {
        'text': tweet.css('[data-testid="tweetText"]::text').get(),
        'author': tweet.css('[data-testid="User-Name"]::text').get(),
        'likes': tweet.css('[data-testid="like"]::text').get(),
        'retweets': tweet.css('[data-testid="retweet"]::text').get()
    }
    print(data)
```

**技巧**：
- ✅ 搜索页面部分公开，无需登录
- ✅ 用 Nitter 实例（Twitter 镜像站）
- ✅ 提取文本后用 POI 技能识别地点

**备选方案：Nitter 镜像**
```python
# Nitter 是 Twitter 开源镜像，无需登录
nitter_instances = [
    'https://nitter.net',
    'https://nitter.privacydev.net',
    'https://nitter.lunar.icu'
]

for instance in nitter_instances:
    url = f'{instance}/search?q=travel%20spot'
    page = fetcher.fetch(url)
    # 提取推文...
```

---

### 3. YouTube

**挑战**：动态加载、反爬

**Scrapling 方案**：
```python
from scrapling.fetchers import DynamicFetcher

fetcher = DynamicFetcher(adaptive=True)

# 搜索结果
url = 'https://www.youtube.com/results?search_query=travel+guide'
page = fetcher.fetch(url)

# 等待视频加载
page.wait_for_selector('#video-title')

videos = page.css('#video-title-link', adaptive=True)

for video in videos:
    data = {
        'title': video.css('#video-title::attr(title)').get(),
        'url': video.css('#video-title::attr(href)').get(),
        'channel': video.css('#channel-name::text').get(),
        'views': video.css('#view-count::text').get()
    }
    print(data)
```

**技巧**：
- ✅ DynamicFetcher 处理动态加载
- ✅ 搜索页面无需登录
- ✅ 用 RSS 源获取频道视频（完全公开）

**备选方案：RSS 源**
```python
# YouTube 频道 RSS（完全公开，无需 API）
channel_id = "UCxxxxxxxxxxxxx"
rss_url = f"https://www.youtube.com/feeds/videos.xml?channel_id={channel_id}"

import requests
response = requests.get(rss_url)
# 解析 XML 获取视频列表
```

---

### 4. TikTok

**挑战**：反爬严格、登录墙

**Scrapling 方案**：
```python
from scrapling.fetchers import StealthyFetcher

fetcher = StealthyFetcher(
    adaptive=True,
    headless=True,
    proxy=None  # 如有代理可配置
)

# 搜索页面
url = 'https://www.tiktok.com/search?q=travel%20spot'
page = fetcher.fetch(url)

videos = page.css('.video-item, .list-item', adaptive=True)

for video in videos:
    data = {
        'desc': video.css('.video-desc::text').get(),
        'author': video.css('.author-name::text').get(),
        'likes': video.css('.like-count::text').get(),
        'comments': video.css('.comment-count::text').get()
    }
    print(data)
```

**备选方案**：
- ✅ 用 TikTok 网页版搜索（部分公开）
- ✅ 用第三方镜像站
- ✅ 从 Instagram Reels 获取类似内容

---

## POI 提取集成

### 使用已有技能

```python
import sys
sys.path.insert(0, '/Users/ssd/.openclaw/workspace/skills/poi-extractor')

from poi_extractor import POIExtractor

extractor = POIExtractor()

# 处理爬取的数据
post = {
    'title': '三亚亚龙湾太美了！',
    'content': '推荐住丽思卡尔顿酒店，去了蜈支洲岛',
    'comments': [
        {'content': '海棠湾免税店在哪？', 'likes': 30}
    ],
    'likes': 1500
}

pois = extractor.extract_from_post(post)

for poi in pois:
    print(f"{poi.poi_name} ({poi.poi_type}) - {poi.city}")
```

### 输出格式

```json
{
  "timestamp": "2026-03-15T02:00:00+08:00",
  "source": "xiaohongshu",
  "pois": [
    {
      "poi_name": "三亚亚龙湾",
      "city": "三亚",
      "poi_type": "景点",
      "confidence": 0.8,
      "heat_score": 1500,
      "source_text": "三亚亚龙湾太美了！"
    },
    {
      "poi_name": "丽思卡尔顿酒店",
      "city": "三亚",
      "poi_type": "住宿",
      "confidence": 0.7,
      "heat_score": 1500
    }
  ]
}
```

---

## 免费地图 API 补全（可选）

### 高德地图（5000 次/日免费）

```python
import requests

AMAP_KEY = "你的 Key"  # 免费注册获取

def get_location(poi_name, city):
    """获取 POI 经纬度"""
    url = "https://restapi.amap.com/v3/place/text"
    params = {
        "keywords": poi_name,
        "city": city,
        "key": AMAP_KEY,
        "offset": 1
    }
    response = requests.get(url, params=params)
    data = response.json()
    
    if data.get("pois"):
        poi = data["pois"][0]
        return {
            "location": poi["location"],  # "经度，纬度"
            "address": poi["address"],
            "type": poi["type"]
        }
    return None
```

**注册**：https://lbs.amap.com

---

### OpenStreetMap（完全免费）

```python
import requests

def osm_search(query):
    """OpenStreetMap 搜索"""
    url = "https://nominatim.openstreetmap.org/search"
    params = {
        "q": query,
        "format": "json",
        "limit": 1
    }
    headers = {"User-Agent": "MyPOIScraper/1.0"}
    response = requests.get(url, params=params, headers=headers)
    data = response.json()
    
    if data:
        return {
            "lat": data[0]["lat"],
            "lon": data[0]["lon"],
            "display_name": data[0]["display_name"]
        }
    return None

# 使用
result = osm_search("三亚亚龙湾")
print(result)
```

---

## 完整爬虫脚本

```python
#!/usr/bin/env python3
# /Users/ssd/.openclaw/workspace/scripts/free-social-scraper.py

import sys
import json
from datetime import datetime
from pathlib import Path

# 添加 Scrapling
from scrapling.fetchers import StealthyFetcher, DynamicFetcher

# 添加 POI 提取器
sys.path.insert(0, '/Users/ssd/.openclaw/workspace/skills/poi-extractor')
from poi_extractor import POIExtractor


class SocialPOIScraper:
    """社交媒体 POI 爬取器"""
    
    def __init__(self):
        self.stealth_fetcher = StealthyFetcher(adaptive=True, headless=True)
        self.dynamic_fetcher = DynamicFetcher(adaptive=True)
        self.poi_extractor = POIExtractor()
        self.data_dir = Path("/Users/ssd/.openclaw/workspace/data")
        self.data_dir.mkdir(exist_ok=True)
    
    def scrape_xiaohongshu(self, keyword="旅行打卡"):
        """爬取小红书"""
        print(f"\n📕 爬取小红书：{keyword}")
        
        url = f'https://www.xiaohongshu.com/search_result?keyword={keyword}'
        page = self.stealth_fetcher.fetch(url)
        
        notes = page.css('.note-item, .search-result-item', adaptive=True)
        posts = []
        
        for note in notes[:20]:  # 限制 20 条
            post = {
                'title': note.css('.title::text').get() or "",
                'content': note.css('.desc::text').get() or "",
                'author': note.css('.nickname::text').get() or "",
                'likes': self._parse_count(note.css('.like-count::text').get()),
                'source': 'xiaohongshu'
            }
            posts.append(post)
        
        return posts
    
    def scrape_twitter(self, keyword="travel spot"):
        """爬取 Twitter（用 Nitter 镜像）"""
        print(f"\n🐦 爬取 Twitter：{keyword}")
        
        nitter_url = f'https://nitter.net/search?q={keyword}'
        page = self.stealth_fetcher.fetch(nitter_url)
        
        tweets = page.css('.tweet', adaptive=True)
        posts = []
        
        for tweet in tweets[:20]:
            post = {
                'content': tweet.css('.tweet-content::text').get() or "",
                'author': tweet.css('.fullname::text').get() or "",
                'likes': self._parse_count(tweet.css('.icon-heart').parent().css('::text').get()),
                'source': 'twitter'
            }
            posts.append(post)
        
        return posts
    
    def scrape_youtube(self, keyword="travel guide"):
        """爬取 YouTube"""
        print(f"\n📺 爬取 YouTube：{keyword}")
        
        url = f'https://www.youtube.com/results?search_query={keyword.replace(" ", "+")}'
        page = self.dynamic_fetcher.fetch(url)
        page.wait_for_selector('#video-title')
        
        videos = page.css('#video-title-link', adaptive=True)
        posts = []
        
        for video in videos[:20]:
            post = {
                'title': video.css('#video-title::attr(title)').get() or "",
                'channel': video.css('#channel-name::text').get() or "",
                'views': self._parse_count(video.css('#view-count::text').get()),
                'url': video.css('#video-title::attr(href)').get() or "",
                'source': 'youtube'
            }
            posts.append(post)
        
        return posts
    
    def scrape_tiktok(self, keyword="travel"):
        """爬取 TikTok"""
        print(f"\n🎵 爬取 TikTok：{keyword}")
        
        url = f'https://www.tiktok.com/search?q={keyword}'
        page = self.stealth_fetcher.fetch(url)
        
        videos = page.css('.video-item, .list-item', adaptive=True)
        posts = []
        
        for video in videos[:20]:
            post = {
                'desc': video.css('.video-desc::text').get() or "",
                'author': video.css('.author-name::text').get() or "",
                'likes': self._parse_count(video.css('.like-count::text').get()),
                'source': 'tiktok'
            }
            posts.append(post)
        
        return posts
    
    def extract_pois(self, posts):
        """从帖子中提取 POI"""
        print(f"\n🔍 提取 POI...")
        
        all_pois = []
        for post in posts:
            pois = self.poi_extractor.extract_from_post(post)
            all_pois.extend(pois)
        
        # 去重
        unique_pois = {}
        for poi in all_pois:
            key = f"{poi.poi_name}_{poi.city}"
            if key not in unique_pois:
                unique_pois[key] = poi
            elif poi.confidence > unique_pois[key].confidence:
                unique_pois[key] = poi
        
        return list(unique_pois.values())
    
    def save_results(self, pois):
        """保存结果"""
        timestamp = datetime.now().strftime("%Y-%m-%d_%H%M")
        filename = self.data_dir / f"poi_{timestamp}.json"
        
        data = {
            "timestamp": datetime.now().isoformat(),
            "count": len(pois),
            "pois": [
                {
                    "poi_name": poi.poi_name,
                    "city": poi.city,
                    "province": poi.province,
                    "poi_type": poi.poi_type,
                    "heat_score": poi.heat_score,
                    "confidence": poi.confidence,
                    "source_text": poi.source_text
                }
                for poi in pois
            ]
        }
        
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        
        print(f"\n💾 保存到：{filename}")
        return filename
    
    def _parse_count(self, text):
        """解析数字（如 1.2 万 → 12000）"""
        if not text:
            return 0
        text = text.strip().lower()
        if '万' in text:
            return int(float(text.replace('万', '')) * 10000)
        elif 'k' in text:
            return int(float(text.replace('k', '')) * 1000)
        else:
            try:
                return int(''.join(filter(str.isdigit, text)))
            except:
                return 0
    
    def run(self, keyword="旅行打卡"):
        """运行完整爬取流程"""
        print("="*60)
        print("🚀 社交媒体 POI 爬取器 - 免费方案")
        print("="*60)
        
        # 爬取各平台
        all_posts = []
        
        try:
            all_posts.extend(self.scrape_xiaohongshu(keyword))
        except Exception as e:
            print(f"❌ 小红书爬取失败：{e}")
        
        try:
            all_posts.extend(self.scrape_twitter(keyword))
        except Exception as e:
            print(f"❌ Twitter 爬取失败：{e}")
        
        try:
            all_posts.extend(self.scrape_youtube(keyword))
        except Exception as e:
            print(f"❌ YouTube 爬取失败：{e}")
        
        try:
            all_posts.extend(self.scrape_tiktok(keyword))
        except Exception as e:
            print(f"❌ TikTok 爬取失败：{e}")
        
        print(f"\n✅ 共爬取 {len(all_posts)} 条内容")
        
        # 提取 POI
        pois = self.extract_pois(all_posts)
        print(f"✅ 提取 {len(pois)} 个 POI")
        
        # 保存结果
        self.save_results(pois)
        
        # 打印摘要
        print("\n" + "="*60)
        print("📊 POI 摘要")
        print("="*60)
        for i, poi in enumerate(pois[:10], 1):
            print(f"{i}. {poi.poi_name} ({poi.poi_type}) - {poi.city}")
        
        return pois


if __name__ == "__main__":
    scraper = SocialPOIScraper()
    scraper.run(keyword="三亚旅行")
```

---

## 定时任务配置

### macOS LaunchAgent

```bash
cat > ~/Library/LaunchAgents/social-poi-scraper.plist << 'EOF'
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
        <string>/Users/ssd/.openclaw/workspace/scripts/free-social-scraper.py</string>
    </array>
    
    <key>WorkingDirectory</key>
    <string>/Users/ssd/.openclaw/workspace</string>
    
    <key>StandardOutPath</key>
    <string>/tmp/poi-scraper-stdout.log</string>
    
    <key>StandardErrorPath</key>
    <string>/tmp/poi-scraper-stderr.log</string>
    
    <key>StartInterval</key>
    <integer>21600</integer>
    
    <key>RunAtLoad</key>
    <true/>
</dict>
</plist>
EOF

launchctl load ~/Library/LaunchAgents/social-poi-scraper.plist
```

### Linux Crontab

```bash
crontab -e

# 每 6 小时执行
0 */6 * * * cd /Users/ssd/.openclaw/workspace && \
    python3 scripts/free-social-scraper.py >> /tmp/poi-scraper.log 2>&1
```

---

## 成本总结

| 项目 | 成本 |
|------|------|
| Scrapling | ✅ 免费 |
| POI 提取技能 | ✅ 免费 |
| 高德 API | ✅ 5000 次/日免费 |
| OpenStreetMap | ✅ 完全免费 |
| 定时任务 | ✅ 系统自带 |
| 数据存储 | ✅ 本地 JSON |
| **总计** | **¥0** |

---

## 下一步

1. **安装 Scrapling**：
   ```bash
   pip install "scrapling[all]"
   scrapling install
   ```

2. **测试爬取**：
   ```bash
   python3 /Users/ssd/.openclaw/workspace/scripts/free-social-scraper.py
   ```

3. **配置定时任务**：
   ```bash
   launchctl load ~/Library/LaunchAgents/social-poi-scraper.plist
   ```

4. **查看结果**：
   ```bash
   ls -lh /Users/ssd/.openclaw/workspace/data/
   cat /Users/ssd/.openclaw/workspace/data/poi_*.json | head -50
   ```

---

_完全免费，无需任何付费 API！_
