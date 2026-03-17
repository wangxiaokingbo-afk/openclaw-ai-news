#!/usr/bin/env python3
"""
热点资讯抓取脚本 v1.0
强制使用 browser 工具执行真实抓取
"""

import subprocess
import sys
import json
from datetime import datetime

def run_agent_task(task_description):
    """通过 openclaw agent 执行任务"""
    cmd = ["openclaw", "agent", "--task", task_description]
    result = subprocess.run(cmd, capture_output=True, text=True, timeout=600)
    return result.stdout + result.stderr

def main():
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M")
    time_slot = datetime.now().strftime("%H%M")
    
    # 明确的任务描述，强制使用 browser 工具
    task = f"""执行热点资讯抓取和推送任务

【强制要求 - 必须使用 browser 工具】
1. 使用 browser 工具 + chrome profile 登录 X 平台 (@wang9067)
   - 搜索关键词：AI, artificial intelligence, 新能源，地缘政治，金融，投资
   - 排序：top + latest 综合
   - 时间范围：最近 3-7 天
   - 记录每条的 like/repost/reply/view 数

2. 使用 browser 工具访问 https://www.newsminimalist.com
   - 抓取 significance >= 5.2 的新闻
   - 记录原媒体链接和 significance 分数

3. 使用 browser 工具访问 YouTube 首页 trending
   - 只抓播客 (Podcasts) 和新闻 (News)
   - 订阅数 > 10 万的频道
   - 时长 > 10 分钟的视频

4. 使用 web_search 补充权威媒体报道

【内容筛选】
- AI: 5 条 (50%) - 排除学习/教程类
- 新能源：3 条 (30%) - 技术突破、市场动态
- 商业金融：1 条 (10%) - 科技巨头、投资并购
- 社会政治：1 条 (10%) - 地缘政治、战争、政策

【报告格式】
- Markdown: reports/daily-top10-{datetime.now().strftime("%Y-%m-%d")}-{time_slot}.md
- HTML: reports/daily-top10-{datetime.now().strftime("%Y-%m-%d")}-{time_slot}.html
- 每条必须包含：标题 + 要点 + 锐评
- 锐评必须有独立观点和判断

【推送】
- 发送钉钉 ActionCard 到群聊 cidwdUjqhs0Pc+p2nKu4pHyVQ==
- 核心结论 10 条置顶
- 精选资讯 5 条详情（含要点 + 锐评）
- 完整报告链接置底

【禁止】
- ❌ 不能编造数据
- ❌ 不能用模拟数据
- ❌ 必须执行真实 browser 抓取
- ❌ 不用 The Verge
- ❌ X 平台不搜 Tesla

当前时间：{timestamp}
"""
    
    print(f"[{timestamp}] 开始执行热点资讯抓取...")
    print(f"[{timestamp}] 任务描述已发送给子 agent")
    
    # 注意：这里不直接执行，而是让主 agent 通过 sessions_spawn 执行
    # 因为需要 browser 工具访问 chrome profile
    print(task)

if __name__ == "__main__":
    main()
