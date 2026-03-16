#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
小红书真实数据抓取 + 广义 POI 提取 - 完整流程
从浏览器获取真实数据，生成 CSV
"""

import json
import csv
from datetime import datetime
from pathlib import Path
from dataclasses import dataclass, asdict, fields

# 从浏览器 snapshot 提取的真实数据
REAL_XHS_DATA = [
    {"title": "已经开始期待五月的新疆了😭真的太美了", "author": "秀清", "likes": 2165, "link": "https://www.xiaohongshu.com/explore/69b1619a000000000c009e9a"},
    {"title": "已经开始期待宫崎骏动漫里的夏天🌲", "author": "麻雀森林厨房", "likes": 9766, "link": "https://www.xiaohongshu.com/explore/69a3f5fa000000001502073a"},
    {"title": "第一次坐香港直达南昌的高铁，被震惊到了", "author": "范糯糯", "likes": 5170, "link": "https://www.xiaohongshu.com/explore/69aecc43000000001503b917"},
    {"title": "最好的人生是赚美元在中国生活", "author": "岛上的夏奈", "likes": 387, "link": "https://www.xiaohongshu.com/explore/69b235ea000000001b0171dc"},
    {"title": "Lake Powell🚢在漂亮的地方真的会变漂亮🥹", "author": "sky 盖盖", "likes": 1409, "link": "https://www.xiaohongshu.com/explore/69b1845b000000001b015f2d"},
    {"title": "大狼屋太贵了！👉去瀑布玩水攻略一定要看", "author": "麻酱", "likes": 352, "link": "https://www.xiaohongshu.com/explore/64aac18d000000002b039f21"},
    {"title": "超爱长岛 | 一直向东你就到了纽约的尽头", "author": "李世琋 Lili", "likes": 107, "link": "https://www.xiaohongshu.com/explore/64a2046800000000120318e9"},
    {"title": "清迈｜想玩水不一定要去海边", "author": "im.atom", "likes": 117, "link": "https://www.xiaohongshu.com/explore/64a96ebd000000002301d881"},
    {"title": "七月第一天🎈", "author": "dcarolx", "likes": 72, "link": "https://www.xiaohongshu.com/explore/64a1782a000000000703b557"},
    {"title": "Mini Vlog11｜海岛日记 🌊", "author": "Yiyi_只兔子", "likes": 183, "link": "https://www.xiaohongshu.com/explore/649cbc08000000001300a613"},
    {"title": "阿那亚买手店也太好逛啦🤭该空着箱子来", "author": "MEIJIE 美界", "likes": 125, "link": "https://www.xiaohongshu.com/explore/64a067ba0000000013014061"},
    {"title": "一些济州岛的照片 (^_^)", "author": "haha_vea🌲", "likes": 2810, "link": "https://www.xiaohongshu.com/explore/69ad5853000000002603036c"},
    {"title": "新西兰不愧是兵家不争之地🇳🇿", "author": "菲比 Phoebe", "likes": 7615, "link": "https://www.xiaohongshu.com/explore/699847ca000000001d02459e"},
    {"title": "我在世外桃源，你们呢🍃", "author": "三木三木呢", "likes": 458, "link": "https://www.xiaohongshu.com/explore/6999aff7000000000a02c8b6"},
    {"title": "海边怎么就去不够呢？！！", "author": "小猪姐姐 zz", "likes": 525, "link": "https://www.xiaohongshu.com/explore/69905281000000000a02a519"},
    {"title": "golden hour🌺💛", "author": "NopeAri", "likes": 2139, "link": "https://www.xiaohongshu.com/explore/69a56f02000000001a02ead5"},
    {"title": "开启度假模式", "author": "钟雅婷", "likes": 8362, "link": "https://www.xiaohongshu.com/explore/69981cf7000000001a029062"},
    {"title": "🌼我的家乡已开满了油菜花！", "author": "渝丸丸丸子", "likes": 640, "link": "https://www.xiaohongshu.com/explore/69a83b89000000001600aac8"},
    {"title": "鼋头渚樱花今日实况，附保姆级攻略", "author": "墨星✨繁天", "likes": 1781, "link": "https://www.xiaohongshu.com/explore/69ad71c2000000002202ca01"},
    {"title": "海边日记本𓇼 ⋆.˚ 𓆝⋆.˚ 🐚", "author": "煮土豆儿", "likes": 18000, "link": "https://www.xiaohongshu.com/explore/69a5285500000000150328ca"},
    {"title": "总有一天你会来到圣米歇尔山⛰️", "author": "乔一乔丶", "likes": 4743, "link": "https://www.xiaohongshu.com/explore/699e89b600000000150217cf"},
    {"title": "Sanya photo dump🐬 𓇼𓈒🥥", "author": "小欣日和", "likes": 1774, "link": "https://www.xiaohongshu.com/explore/69aeae4a0000000022039873"},
    {"title": "三亚｜爱一万次海边的日落", "author": "我要早睡", "likes": 4334, "link": "https://www.xiaohongshu.com/explore/699daaab0000000028021b09"},
    {"title": "吉隆坡双子塔#东南亚旅游 #吉隆坡双子塔 #", "author": "瑞哥英语_RyanChen", "likes": 3925, "link": "https://www.xiaohongshu.com/explore/699c26c8000000000d0089a9"},
]

CITIES = ["新疆", "香港", "南昌", "纽约", "清迈", "济州岛", "新西兰", "阿那亚", "三亚", "吉隆坡", "鼋头渚", "圣米歇尔山"]

@dataclass
class POI:
    poi_name: str
    main_poi: str
    poi_type: str
    poi_category: str
    city: str
    heat_score: float
    source_text: str
    source_type: str
    confidence: float

def detect_city(title):
    for city in CITIES:
        if city in title:
            return city
    return "未知"

def extract_poi(title, city):
    """从标题提取 POI"""
    pois = []
    
    # 提取主 POI（地名 + 后续）
    if city in title:
        idx = title.find(city)
        following = title[idx:idx+20]
        for sep in ['😭', '🌲', '｜', '🇳🇿', '🌺', '💛', '🐬', '𓇼', '⛰️', '🌼']:
            if sep in following:
                pos = following.find(sep)
                if pos > 2:
                    following = following[:pos]
                    break
        if 3 <= len(following) <= 20:
            pois.append({
                "name": following,
                "main_poi": following,
                "type": "景点" if any(k in following for k in ["山", "海", "湖", "岛", "谷"]) else "其他",
                "category": "导航类"
            })
    
    return pois

def main():
    print("="*70)
    print("🎯 小红书真实数据 - 广义 POI 提取")
    print("="*70)
    
    all_pois = []
    
    for post in REAL_XHS_DATA:
        title = post["title"]
        likes = post["likes"]
        city = detect_city(title)
        
        pois = extract_poi(title, city)
        for poi in pois:
            poi_obj = POI(
                poi_name=poi["name"],
                main_poi=poi["main_poi"],
                poi_type=poi["type"],
                poi_category=poi["category"],
                city=city,
                heat_score=float(likes),
                source_text=title,
                source_type="post_title",
                confidence=0.85
            )
            all_pois.append(poi_obj)
    
    print(f"\n✅ 提取到 {len(all_pois)} 个 POI\n")
    
    # 导出 CSV
    output_dir = Path("xhs_lx/xhs_lx")
    output_dir.mkdir(exist_ok=True)
    
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    csv_file = output_dir / f"xhs_real_poi_{timestamp}.csv"
    
    with open(csv_file, 'w', encoding='utf-8-sig', newline='') as f:
        fieldnames = [field.name for field in fields(POI)]
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        for poi in all_pois:
            writer.writerow(asdict(poi))
    
    print(f"💾 CSV 已保存：{csv_file}")
    
    # 展示结果
    print("\n📊 POI 列表:")
    for i, poi in enumerate(all_pois[:20], 1):
        print(f"{i:2}. {poi.poi_name:20} | {poi.city:6} | 热度:{poi.heat_score:6.0f}")
    
    if len(all_pois) > 20:
        print(f"... 还有 {len(all_pois)-20} 个")
    
    print("="*70)
    
    return str(csv_file)

if __name__ == "__main__":
    main()
