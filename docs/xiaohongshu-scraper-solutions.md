# 小红书数据获取方案对比

_最后更新：2026-03-15 01:35_

---

## 快速结论

| 方案 | 类型 | 免登录 | 成熟度 | 成本 | 推荐度 |
|------|------|--------|--------|------|--------|
| **TikHub API** | 商业 API | ✅ 是 | ⭐⭐⭐⭐⭐ | 付费 | 🟢 最佳 |
| **lxSpider** | 开源项目 | ⚠️ 需 Cookie | ⭐⭐⭐⭐ | 免费 | 🟢 推荐 |
| **redbooks** | 开源工具 | ⚠️ 需登录 | ⭐⭐⭐ | 免费 | 🟡 可用 |
| **TikHub SDK** | Python SDK | ✅ 是 | ⭐⭐⭐⭐⭐ | 付费 | 🟢 最佳 |

---

## 方案一：TikHub API（⭐ 强烈推荐）

**项目**：[TikHub/TikHub-API-Python-SDK](https://github.com/TikHub/TikHub-API-Python-SDK)  
**Stars**: 599 | **语言**: Python

### 核心优势

| 特性 | 说明 |
|------|------|
| ✅ **免登录** | 基于 API 调用，无需自己维护 Cookie |
| ✅ **多平台** | 抖音、TikTok、小红书、快手、微博、Instagram、YouTube、Twitter |
| ✅ **高可用** | 专业团队维护，SLA 保障 |
| ✅ **完整数据** | 笔记详情、评论、点赞、收藏、用户信息 |
| ✅ **Python SDK** | 异步高性能，开箱即用 |

### 支持的接口

| 平台 | 接口类型 |
|------|---------|
| 小红书 | 网页版 API |
| 抖音 | App V1/V2/V3 + 网页版 |
| TikTok | App V2/V3 + 网页版 |
| 快手 | 网页版 |
| 微博 | 网页版 |
| Instagram | Web + App |
| YouTube | Web |
| Twitter/X | Web |
| 验证码 | 自动识别 |
| 临时邮箱 | 接码服务 |

### 使用示例

```python
from tikhub import Client

client = Client(
    base_url="https://api.tikhub.io",
    api_key="YOUR_API_TOKEN",
    max_retries=3,
    timeout=60
)

# 获取小红书笔记详情
note_data = await client.XiaohongshuWeb.fetch_note_detail(note_id="xxx")
print(note_data)

# 获取评论
comments = await client.XiaohongshuWeb.fetch_note_comments(note_id="xxx")
print(comments)
```

### 价格

**计费模式**：按调用量计费（预付费余额制）

- **免费额度**：注册送测试额度（具体金额需登录后台查看）
- **单价**：每个 API 端点独立定价，约 $0.001-$0.01/次
- **阶梯折扣**：用量越大折扣越高
- **查询价格**：SDK 支持 `calculate_price()` 提前计算

**查询方法**：
```python
# 计算每日 100 次调用的价格
price = await client.TikHubUser.calculate_price(
    endpoint="/api/v1/xiaohongshu/web/fetch_note_detail",
    request_per_day=100
)
print(price)

# 获取阶梯折扣信息
tiered_discount_info = await client.TikHubUser.get_tiered_discount_info()
```

**文档**：https://docs.tikhub.io/  
**API 测试**：https://api.tikhub.io  
**后台**：https://beta-web.tikhub.io

### 获取 Token

1. 注册：https://beta-web.tikhub.io/users/api_keys
2. 生成 API Token
3. 设置权限和过期时间

---

## 方案二：lxSpider（⭐ 推荐）

**项目**：[lixi5338619/lxSpider](https://github.com/lixi5338619/lxSpider)  
**Stars**: 1,902 | **Forks**: 460 | **语言**: Python

### 核心优势

| 特性 | 说明 |
|------|------|
| ✅ **超全平台** | 淘宝、京东、抖音、快手、微博、微信、小红书、知乎、推特等 |
| ✅ **高 Star** | 1902 stars，社区认可度高 |
| ✅ **持续更新** | 最后更新：2026-03-14 |
| ⚠️ **需 Cookie** | 需要自己获取并维护 Cookie |

### 支持平台（部分）

```
淘宝、京东、天猫、豆瓣、抖音、快手、微博、微信、阿里、头条、
pdd、优酷、爱奇艺、携程、12306、58、搜狐、各种指数、
维普万方、Zlibrary、Oalib、小说、招标网、采购网、
小红书、大众点评、推特、脉脉、知乎
```

### 使用方式

```python
# 需要查看项目具体实现
# 通常需要配置 Cookie
import lxSpider

spider = lxSpider.Xiaohongshu(cookie="your_cookie")
data = spider.get_note("note_id")
```

### 优缺点

**优点**：
- 免费开源
- 支持平台极多
- 社区活跃

**缺点**：
- 需要自己维护 Cookie
- Cookie 过期需手动更新
- 可能需要处理验证码

---

## 方案三：redbooks（可用）

**项目**：[xiaofuqing13/redbooks](https://github.com/xiaofuqing13/redbooks)  
**Stars**: 5 | **语言**: Python

### 核心功能

| 功能 | 说明 |
|------|------|
| 爬取模式 | 标准模式（完整数据）、极速模式（快速采集） |
| 爬取类型 | 关键词搜索、主页推荐、博主主页 |
| 数据采集 | 标题、作者、正文、标签、发布时间、IP 地区、互动数据 |
| 媒体下载 | 图片批量下载、视频下载、评论图片 |
| 数据导出 | Excel 导出、SQLite 存储 |
| GUI 界面 | 图形化操作界面 |

### 技术栈

- DrissionPage（浏览器自动化）
- pandas（数据处理）
- openpyxl（Excel 导出）
- Pillow（图片处理）

### 使用方式

```bash
# 安装依赖
pip install -r requirements.txt

# 运行
python crawler_ultimate.py
```

### 优缺点

**优点**：
- 有图形界面，操作简单
- 支持 Excel 导出
- 本地运行，数据自己掌控

**缺点**：
- 需要登录小红书账号
- 仅支持 Windows 10/11
- Star 较少，社区支持有限
- 需要浏览器环境

---

## 方案四：其他开源项目

| 项目 | Stars | 特点 |
|------|-------|------|
| [Tangerineeew/Selenium-basedXiaohongshuCrawler](https://github.com/Tangerineeew/Selenium-basedXiaohongshuCrawler) | 50 | Selenium 模拟浏览器 |
| [mcxiaoxiao/xiaohongshuCrawler](https://github.com/mcxiaoxiao/xiaohongshuCrawler) | 49 | 简易爬虫，三步实现 |
| [KaitoHH/xiaohongshu-spider-visualizer](https://github.com/KaitoHH/xiaohongshu-spider-visualizer) | 32 | 分布式爬虫 + 可视化 |
| [jiawei666/xiaohongshu_app_crawler](https://github.com/jiawei666/xiaohongshu_app_crawler) | 29 | APP 爬虫实现 |
| [upJiang/jiang-xiaohongshu-crawler](https://github.com/upJiang/jiang-xiaohongshu-crawler) | 8 | Puppeteer + AI 舆情分析 |

---

## 方案五：商业数据平台（企业级）

| 平台 | 服务 | 价格 |
|------|------|------|
| **飞瓜数据** | 小红书榜单、达人分析、内容监控 | 付费，数千元/年 |
| **新红** | 小红书数据分析平台 | 付费 |
| **蝉妈妈** | 直播电商数据分析 | 付费 |

---

## 推荐方案对比

### 个人开发者/小团队

**首选：TikHub API**
- 免登录，无需维护 Cookie
- Python SDK 开箱即用
- 按量付费，成本低
- 多平台支持

**备选：lxSpider**
- 免费开源
- 需要自己维护 Cookie
- 适合有技术能力的开发者

### 企业用户

**首选：TikHub API + 商业数据平台**
- TikHub 用于实时数据获取
- 飞瓜/新红用于行业分析

**备选：定制开发**
- 基于 lxSpider 或 redbooks 二次开发
- 部署到自有服务器

---

## 集成到 OpenClaw

### 方案 A：使用 TikHub SDK（推荐）

1. **安装 SDK**：
```bash
pip install tikhub
```

2. **配置 API Key**：
```bash
openclaw configure --set TIKHUB_API_KEY=你的_key
```

3. **创建技能**：
- 封装 TikHub API 为 OpenClaw 技能
- 支持自然语言查询

### 方案 B：集成 lxSpider

1. **克隆项目**：
```bash
git clone https://github.com/lixi5338619/lxSpider.git
```

2. **配置 Cookie**：
- 手动获取小红书 Cookie
- 配置到环境变量

3. **创建技能**：
- 封装为 OpenClaw 技能

---

## 数据字段对比

| 字段 | TikHub | lxSpider | redbooks |
|------|--------|----------|----------|
| 笔记标题 | ✅ | ✅ | ✅ |
| 正文内容 | ✅ | ✅ | ✅ |
| 作者信息 | ✅ | ✅ | ✅ |
| 发布时间 | ✅ | ✅ | ✅ |
| IP 地区 | ✅ | ✅ | ✅ |
| 点赞数 | ✅ | ✅ | ✅ |
| 收藏数 | ✅ | ✅ | ✅ |
| 评论数 | ✅ | ✅ | ✅ |
| 评论列表 | ✅ | ⚠️ | ✅ |
| 图片链接 | ✅ | ✅ | ✅ |
| 视频链接 | ✅ | ✅ | ✅ |
| 标签 | ✅ | ✅ | ✅ |

---

## 最终建议

### 🏆 最佳方案：TikHub API

**理由**：
1. 免登录，无需维护 Cookie
2. 专业团队维护，稳定性高
3. Python SDK 易用
4. 支持多平台（抖音、TikTok、小红书等）
5. 按量付费，成本可控

**适合**：个人开发者、小团队、企业

### 🥈 备选方案：lxSpider

**理由**：
1. 免费开源
2. 支持平台极多
3. 社区活跃（1902 stars）

**适合**：有技术能力、想免费的开发者

---

## 下一步

1. **注册 TikHub**：https://beta-web.tikhub.io
2. **获取 API Token**
3. **测试 API**：https://api.tikhub.io
4. **集成到 OpenClaw**（需要我帮你创建技能）

---

_需要我帮你创建 TikHub 集成技能吗？_
