#!/usr/bin/env python3
"""
网页抓取脚本 - 使用 URL 转 Markdown 服务
支持多种服务：markdown.new, defuddle.md, r.jina.ai
"""

import sys
import urllib.request
import urllib.parse
import ssl

SERVICES = [
    ("markdown.new", "https://markdown.new/{}"),
    ("defuddle.md", "https://defuddle.md/{}"),
    ("r.jina.ai", "https://r.jina.ai/{}"),
]

def fetch_url(url: str) -> tuple[str, str]:
    """尝试用不同服务抓取网页，返回 (service_name, content)"""
    
    # 创建 SSL 上下文（忽略证书验证问题）
    ctx = ssl.create_default_context()
    ctx.check_hostname = False
    ctx.verify_mode = ssl.CERT_NONE
    
    for service_name, service_template in SERVICES:
        try:
            target_url = service_template.format(url)
            req = urllib.request.Request(
                target_url,
                headers={'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36'}
            )
            with urllib.request.urlopen(req, timeout=10, context=ctx) as response:
                content = response.read().decode('utf-8')
                return service_name, content.strip()
        except Exception as e:
            print(f"[{service_name}] 失败：{e}", file=sys.stderr)
            continue
    
    return None, f"所有服务都失败了，请尝试手动访问或使用 Scrapling 爬虫工具"

def main():
    if len(sys.argv) < 2:
        print("用法：python fetch_page.py <URL>")
        sys.exit(1)
    
    url = sys.argv[1]
    
    # 确保 URL 有协议前缀
    if not url.startswith(('http://', 'https://')):
        url = 'https://' + url
    
    service_name, content = fetch_url(url)
    
    if service_name:
        print(f"使用服务：{service_name}")
        print("-" * 50)
        print(content)
    else:
        print(content)
        sys.exit(1)

if __name__ == "__main__":
    main()
