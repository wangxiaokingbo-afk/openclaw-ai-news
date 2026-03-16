---
name: web-page-fetcher
description: 网页抓取技能 - 使用 URL 转 Markdown 服务快速抓取网页内容。当用户需要获取网页信息、阅读文章、抓取页面内容时使用。支持 markdown.new、defuddle.md、r.jina.ai 三种服务，自动降级备选。
---

# Web Page Fetcher - 网页抓取技能

## 核心思路

**用 URL 转 Markdown 服务代替复杂的搜索工具配置**，让 OpenClaw 能快速抓取网页内容。

## 使用方法

### 方法 1: URL 前缀服务（推荐）

直接在网址前添加服务前缀，浏览器会自动显示 Markdown 版本：

1. **`markdown.new/https://网址`** - Cloudflare 系网站适用（首选）
2. **`defuddle.md/https://网址`** - 通用备选
3. **`r.jina.ai/https://网址`** - 另一个备选

### 方法 2: 使用脚本

```bash
python scripts/fetch_page.py <URL>
```

脚本会自动尝试三种服务，返回第一个成功的内容。

### 方法 3: Scrapling 爬虫（最后备选）

如果以上服务都失败，使用 Scrapling 爬虫工具：
https://github.com/D4Vinci/Scrapling

## 触发场景

当用户说以下类似内容时，使用此技能：

- "抓取这个网页：[URL]"
- "帮我看看这个链接的内容"
- "读取这个网址的信息"
- "把这篇转成文字"
- "这个链接讲了什么"

## 工作流程

1. **检查 URL** - 确保有 `http://` 或 `https://` 前缀
2. **尝试 markdown.new** - 首选服务，速度快
3. **尝试 defuddle.md** - 备选 1
4. **尝试 r.jina.ai** - 备选 2
5. **建议 Scrapling** - 如果都失败

## 注意事项

- 这些服务对大多数网站有效，特别是静态内容
- 动态渲染的网站（需要 JavaScript）可能抓取不完整
- 需要登录的网站无法抓取
- 返回的是 Markdown 格式，便于后续处理

## 示例

**用户**: 抓取这个网页的内容 https://example.com/article

**助手**: 
```
使用服务：markdown.new
--------------------------------------------------
# 文章标题

这里是文章内容...
```
