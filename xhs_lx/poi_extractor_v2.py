#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
小红书数据抓取 + POI 提取优化版 + 高德验证
全流程脚本 v2.0
"""

import json
import re
from datetime import datetime
from pathlib import Path
from dataclasses import dataclass, asdict
from typing import List, Dict


# ==================== POI 提取器（优化版） ====================

@dataclass
class POI:
    poi_name: str
    city: str = ""
    province: str = ""
    poi_type: str = ""
    heat_score: float = 0.0
    source_text: str = ""
    source_type: str = ""
    confidence: float = 0.0


class POIExtractor:
    """POI 提取器 - 优化版"""
    
    # 热门旅游城市
    CITIES = [
        "北京", "上海", "广州", "深圳", "杭州", "成都", "重庆", "西安", "南京", "武汉",
        "三亚", "丽江", "大理", "厦门", "青岛", "大连", "东京", "大阪", "首尔", "济州岛",
        "曼谷", "清迈", "吉隆坡", "新加坡", "悉尼", "墨尔本", "巴黎", "伦敦", "纽约", "洛杉矶",
        "新疆", "西藏", "云南", "四川", "青海", "甘肃", "贵州", "广西", "海南", "台湾"
    ]
    
    # POI 类型词
    POI_TYPE_WORDS = {
        "景点": ["景区", "景点", "公园", "乐园", "海滩", "海岛", "山", "湖", "海", "古镇", "古城", "寺庙"],
        "住宿": ["酒店", "民宿", "宾馆", "客栈", "度假村"],
        "餐饮": ["餐厅", "餐馆", "咖啡馆", "咖啡厅", "奶茶店", "火锅"],
        "交通": ["机场", "火车站", "高铁站", "地铁站", "公交站"],
        "购物": ["商场", "购物中心", "超市", "市场", "免税店"],
    }
    
    def __init__(self):
        self.pois = []
    
    def detect_city(self, text: str) -> str:
        """检测城市"""
        for city in self.CITIES:
            if city in text:
                return city
        return "未知"
    
    def detect_poi_type(self, text: str) -> str:
        """检测 POI 类型"""
        for poi_type, keywords in self.POI_TYPE_WORDS.items():
            for keyword in keywords:
                if keyword in text:
                    return poi_type
        return "其他"
    
    def extract_poi_name(self, text: str, city: str) -> List[str]:
        """
        提取 POI 名称
        
        策略：
        1. 城市/地名 + 后续 2-10 字
        2. 包含类型词的短语
        """
        pois = []
        
        # 策略 1: 城市 + 后续内容
        if city in self.CITIES:
            idx = text.find(city)
            if idx >= 0:
                # 提取城市后最多 15 字
                following = text[idx:idx+18]
                # 在合适的位置截断（标点符号）
                for sep in ['，', '。', ',', '.', '！', '？', '!', '?', ' ', '的', '去', '到', '在']:
                    if sep in following:
                        pos = following.find(sep)
                        if pos > 2:
                            following = following[:pos]
                            break
                if 2 <= len(following) <= 15:
                    pois.append(following)
        
        # 策略 2: 类型词结尾
        all_type_words = sum(self.POI_TYPE_WORDS.values(), [])
        for type_word in all_type_words:
            if type_word in text:
                idx = text.find(type_word)
                # 往前找最多 8 字
                start = max(0, idx - 8)
                prefix = text[start:idx]
                # 从合适的边界开始
                for sep in ['，', '。', ',', '.', ' ', '了', '去', '到', '在']:
                    if sep in prefix:
                        prefix = prefix[prefix.rfind(sep)+1:]
                        break
                poi_name = prefix + type_word
                if 2 <= len(poi_name) <= 15:
                    pois.append(poi_name)
        
        # 去重
        return list(dict.fromkeys(pois))
    
    def calculate_heat(self, likes: int = 0, comments: int = 0) -> float:
        """计算热度"""
        return round(likes * 1.0 + comments * 5.0, 2)
    
    def extract_from_text(self, text: str, source_type: str, likes: int = 0, comments: int = 0) -> List[POI]:
        """从文本中提取 POI"""
        pois = []
        city = self.detect_city(text)
        
        poi_names = self.extract_poi_name(text, city)
        
        for poi_name in poi_names:
            poi = POI(
                poi_name=poi_name,
                city=city,
                poi_type=self.detect_poi_type(poi_name),
                heat_score=self.calculate_heat(likes, comments),
                source_text=text[:100],
                source_type=source_type,
                confidence=0.8 if source_type == "post_title" else 0.6
            )
            pois.append(poi)
        
        return pois
    
    def extract_from_post(self, post: Dict) -> List[POI]:
        """从帖子中提取 POI（包括评论）"""
        all_pois = []
        
        # 1. 从标题提取
        title = post.get("title", "")
        if title:
            pois = self.extract_from_text(title, "post_title", post.get("likes", 0), post.get("comments_count", 0))
            all_pois.extend(pois)
        
        # 2. 从正文提取
        content = post.get("content", "")
        if content:
            pois = self.extract_from_text(content, "post_content", post.get("likes", 0), post.get("comments_count", 0))
            all_pois.extend(pois)
        
        # 3. 从评论提取（重要！）
        comments = post.get("comments", [])
        for comment in comments:
            comment_text = comment.get("content", "")
            comment_likes = comment.get("likes", 0)
            
            if comment_text:
                pois = self.extract_from_text(comment_text, "comment", comment_likes, 0)
                all_pois.extend(pois)
        
        return all_pois
    
    def process_posts(self, posts: List[Dict]) -> List[POI]:
        """批量处理帖子"""
        all_pois = []
        for post in posts:
            pois = self.extract_from_post(post)
            all_pois.extend(pois)
        
        # 去重（相同名称 + 城市）
        unique = {}
        for poi in all_pois:
            key = f"{poi.poi_name}_{poi.city}"
            if key not in unique or poi.confidence > unique[key].confidence:
                unique[key] = poi
        
        self.pois = list(unique.values())
        return self.pois


# ==================== 主流程 ====================

def main():
    """主流程"""
    print("="*70)
    print("🚀 小红书 POI 提取优化版")
    print("="*70)
    
    # 测试数据（模拟从浏览器抓取的真实数据）
    test_posts = [
        {
            "title": "已经开始期待五月的新疆了😭真的太美了",
            "content": "五月的伊犁草原真的太美了，推荐大家去那拉提和喀拉峻。住宿可以选择特克斯县的民宿，很有特色。",
            "comments": [
                {"content": "请问那拉提草原怎么去？从乌鲁木齐有班车吗？", "likes": 50},
                {"content": "独库公路什么时候开通？想去自驾", "likes": 35},
                {"content": "赛里木湖也超美！强烈推荐", "likes": 28},
                {"content": "喀什古城也值得一去，很有异域风情", "likes": 22},
            ],
            "likes": 2165,
            "comments_count": 128
        },
        {
            "title": "第一次坐香港直达南昌的高铁，被震惊到了",
            "content": "香港西九龙站直达南昌，只要 7 个小时！沿途风景很美。准备去滕王阁和八一广场打卡。",
            "comments": [
                {"content": "南昌万达茂的融创乐园好玩吗？", "likes": 15},
                {"content": "推荐去秋水广场看喷泉，晚上很美", "likes": 12},
            ],
            "likes": 5170,
            "comments_count": 256
        },
        {
            "title": "三亚｜爱一万次海边的日落",
            "content": "三亚的海真的看不腻！这次住了海棠湾的亚特兰蒂斯，水族馆超棒。还去了亚龙湾和蜈支洲岛。",
            "comments": [
                {"content": "海棠湾免税店具体位置在哪里？", "likes": 45},
                {"content": "亚龙湾的丽思卡尔顿酒店怎么样？值得住吗？", "likes": 38},
                {"content": "蜈支洲岛的门票多少钱？", "likes": 25},
                {"content": "推荐去大东海，人少景美", "likes": 18},
            ],
            "likes": 4334,
            "comments_count": 189
        }
    ]
    
    # 提取 POI
    print("\n📊 提取 POI...")
    extractor = POIExtractor()
    pois = extractor.process_posts(test_posts)
    
    print(f"✅ 提取到 {len(pois)} 个 POI\n")
    
    # 输出结果
    print("="*70)
    print("📋 POI 列表")
    print("="*70)
    
    for i, poi in enumerate(pois, 1):
        print(f"\n{i}. {poi.poi_name}")
        print(f"   城市：{poi.city}")
        print(f"   类型：{poi.poi_type}")
        print(f"   热度：{poi.heat_score}")
        print(f"   来源：{poi.source_type}")
        print(f"   置信度：{poi.confidence}")
    
    # 保存结果
    output_dir = Path("xhs_lx/xhs_lx")
    output_dir.mkdir(exist_ok=True)
    
    output_file = output_dir / f"poi_optimized_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump([asdict(poi) for poi in pois], f, ensure_ascii=False, indent=2)
    
    print(f"\n💾 结果已保存：{output_file}")
    print("="*70)
    
    return pois


if __name__ == "__main__":
    main()
