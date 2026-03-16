#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
广义 POI 提取器 v3.0
支持标准 POI + 非标准 POI（打卡点/补给点/功能点等）
"""

import re
import json
from typing import List, Dict, Optional
from dataclasses import dataclass, asdict
from datetime import datetime


@dataclass
class POI:
    """广义 POI 数据结构"""
    poi_name: str
    poi_category: str = ""  # 导航类/搜索类/决策类
    poi_type: str = ""  # 景点/拍照点/补给点等
    city: str = ""
    province: str = ""
    location_desc: str = ""  # 位置描述（如"山顶右侧"）
    function_desc: str = ""  # 功能描述（如"看日落"）
    sentiment: str = ""  # 推荐/避雷/中性
    heat_score: float = 0.0
    source_text: str = ""
    source_type: str = ""  # post_title/post_content/comment
    confidence: float = 0.0
    user_intent: str = ""  # 导航/搜索/决策


class GeneralizedPOIExtractor:
    """
    广义 POI 提取器
    
    支持：
    1. 标准 POI（景点/酒店/餐厅）
    2. 非标准 POI（打卡点/拍照点/观景台）
    3. 功能点位（补给点/停车点/洗手间）
    4. 搜索点位（免费/人少/宠物友好）
    """
    
    # ===== 扩展的 POI 类型库 =====
    
    POI_TYPES = {
        # 标准 POI
        "景点": ["景区", "景点", "公园", "乐园", "度假区", "海滩", "海岛", "山", "湖", "海", "瀑布", "森林", "古镇", "古城", "寺庙", "教堂", "博物馆", "动物园", "植物园"],
        "住宿": ["酒店", "民宿", "宾馆", "客栈", "度假村", "青旅", "公寓"],
        "餐饮": ["餐厅", "餐馆", "饭店", "咖啡馆", "咖啡厅", "奶茶店", "小吃店", "烧烤", "火锅", "自助餐"],
        "交通": ["机场", "火车站", "高铁站", "地铁站", "公交站", "码头", "港口"],
        "购物": ["商场", "购物中心", "超市", "市场", "夜市", "商业街"],
        
        # 非标准 POI（新增！）
        "拍照点": ["打卡点", "拍照点", "机位", "观景台", "拍摄点", "取景地", "摄影点"],
        "功能点": ["补给点", "停车点", "露营点", "休息点", "售票处", "入口", "出口", "游客中心"],
        "设施点": ["洗手间", "厕所", "充电桩", "加油站", "饮水处", "储物柜", "行李寄存"],
        "观测点": ["日出观测点", "日落观赏点", "观星点", "观景台", "眺望台"],
    }
    
    # 用户意图关键词
    INTENT_KEYWORDS = {
        "导航": ["怎么去", "在哪", "在哪里", "什么位置", "地址", "路线", "导航", "开车", "地铁", "公交"],
        "搜索": ["免费", "人少", "推荐", "值得", "好玩", "好吃", "必看", "必去", "宠物友好", "不用排队"],
        "决策": ["值得吗", "好玩吗", "坑吗", "避雷", "攻略", "注意事项", "门票", "价格", "开放时间"]
    }
    
    # 情感关键词
    SENTIMENT_KEYWORDS = {
        "推荐": ["推荐", "值得", "必去", "必看", "超美", "绝美", "震撼", "好看", "好玩", "喜欢"],
        "避雷": ["坑", "避雷", "不要去", "不值得", "失望", "贵", "人多", "排队", "踩雷"]
    }
    
    # 地理位置库
    CITIES = [
        "北京", "上海", "广州", "深圳", "杭州", "成都", "重庆", "西安", "南京", "武汉",
        "三亚", "丽江", "大理", "厦门", "青岛", "大连", "东京", "大阪", "首尔", "济州岛",
        "曼谷", "清迈", "吉隆坡", "新加坡", "悉尼", "墨尔本", "巴黎", "伦敦", "纽约", "洛杉矶",
        "新疆", "西藏", "云南", "四川", "青海", "甘肃", "贵州", "广西", "海南", "台湾"
    ]
    
    def __init__(self):
        self.pois = []
    
    def detect_city(self, text: str) -> str:
        """检测城市"""
        for city in self.CITIES:
            if city in text:
                return city
        return "未知"
    
    def detect_poi_type(self, text: str) -> tuple:
        """
        检测 POI 类型
        返回：(category, type)
        """
        for poi_type, keywords in self.POI_TYPES.items():
            for keyword in keywords:
                if keyword in text:
                    # 分类
                    if poi_type in ["景点", "住宿", "餐饮", "交通", "购物"]:
                        category = "导航类"
                    elif poi_type in ["拍照点", "观测点"]:
                        category = "导航类"
                    elif poi_type in ["功能点", "设施点"]:
                        category = "导航类"
                    else:
                        category = "其他"
                    
                    return (category, poi_type)
        
        return ("其他", "其他")
    
    def detect_user_intent(self, text: str) -> str:
        """检测用户意图"""
        for intent, keywords in self.INTENT_KEYWORDS.items():
            for keyword in keywords:
                if keyword in text:
                    return intent
        return "其他"
    
    def detect_sentiment(self, text: str) -> str:
        """检测情感倾向"""
        for sentiment, keywords in self.SENTIMENT_KEYWORDS.items():
            for keyword in keywords:
                if keyword in text:
                    return sentiment
        return "中性"
    
    def extract_poi_name(self, text: str, city: str) -> List[Dict]:
        """
        提取 POI 名称（支持非标准 POI）
        
        返回：[{"name": "", "type": "", "location": "", "function": ""}]
        """
        pois = []
        
        # 策略 1: 城市/地名 + 后续内容
        if city in self.CITIES:
            idx = text.find(city)
            if idx >= 0:
                # 提取城市后最多 20 字
                following = text[idx:idx+25]
                # 在合适位置截断
                for sep in ['，', '。', ',', '.', '！', '？', ' ', '的', '去', '到', '在', '旁边', '附近']:
                    if sep in following:
                        pos = following.find(sep)
                        if pos > 2:
                            following = following[:pos]
                            break
                
                if 2 <= len(following) <= 20:
                    category, poi_type = self.detect_poi_type(following)
                    pois.append({
                        "name": following,
                        "type": poi_type,
                        "category": category,
                        "location": "",
                        "function": ""
                    })
        
        # 策略 2: POI 类型词结尾
        all_type_words = sum(self.POI_TYPES.values(), [])
        for type_word in all_type_words:
            if type_word in text:
                idx = text.find(type_word)
                # 往前找最多 10 字
                start = max(0, idx - 10)
                prefix = text[start:idx]
                
                # 从合适边界开始
                for sep in ['，', '。', ',', '.', ' ', '了', '去', '到', '在', '有个', '看到']:
                    if sep in prefix:
                        prefix = prefix[prefix.rfind(sep)+len(sep):]
                        break
                
                poi_name = prefix + type_word
                
                if 2 <= len(poi_name) <= 20:
                    category, poi_type = self.detect_poi_type(poi_name)
                    
                    # 提取位置描述（如"山顶右侧"）
                    location = ""
                    location_patterns = [
                        r"(?:在|位于|坐落)([^\s,，.。]{2,10}(?:侧 | 边 | 旁 | 顶 | 底 | 口))",
                        r"([^\s,，.。]{2,8}(?:顶 | 底 | 口 | 侧 | 边))"
                    ]
                    for pattern in location_patterns:
                        match = re.search(pattern, text[:idx+20])
                        if match:
                            location = match.group(1)
                            break
                    
                    # 提取功能描述（如"看日落"）
                    function = ""
                    function_patterns = [
                        r"(?:可以 | 能够 | 用来|是)([^\s,，.。]{2,15}(?:看 | 拍 | 观 | 休 | 补))",
                        r"([^\s,，.。]{2,10}(?:看 | 拍 | 观)[^\s,，.。]{0,5})"
                    ]
                    for pattern in function_patterns:
                        match = re.search(pattern, text[idx:idx+30])
                        if match:
                            function = match.group(1)
                            break
                    
                    pois.append({
                        "name": poi_name,
                        "type": poi_type,
                        "category": category,
                        "location": location,
                        "function": function
                    })
        
        # 去重
        unique = []
        seen = set()
        for poi in pois:
            key = poi["name"]
            if key not in seen:
                seen.add(key)
                unique.append(poi)
        
        return unique
    
    def extract_from_text(self, text: str, source_type: str, likes: int = 0, comments: int = 0) -> List[POI]:
        """从文本中提取 POI"""
        pois = []
        city = self.detect_city(text)
        user_intent = self.detect_user_intent(text)
        sentiment = self.detect_sentiment(text)
        
        poi_entities = self.extract_poi_name(text, city)
        
        for poi_entity in poi_entities:
            poi = POI(
                poi_name=poi_entity["name"],
                poi_category=poi_entity["category"],
                poi_type=poi_entity["type"],
                city=city,
                location_desc=poi_entity["location"],
                function_desc=poi_entity["function"],
                sentiment=sentiment,
                heat_score=self._calculate_heat(likes, comments),
                source_text=text[:100],
                source_type=source_type,
                confidence=self._calculate_confidence(source_type, poi_entity, sentiment),
                user_intent=user_intent
            )
            pois.append(poi)
        
        return pois
    
    def _calculate_heat(self, likes: int = 0, comments: int = 0) -> float:
        """计算热度"""
        return round(likes * 1.0 + comments * 5.0, 2)
    
    def _calculate_confidence(self, source_type: str, poi_entity: Dict, sentiment: str) -> float:
        """计算置信度"""
        base = 0.5
        
        # 来源加分
        if source_type == "post_title":
            base += 0.3
        elif source_type == "post_content":
            base += 0.2
        elif source_type == "comment":
            base += 0.1
        
        # 有位置描述加分
        if poi_entity.get("location"):
            base += 0.1
        
        # 有功能描述加分
        if poi_entity.get("function"):
            base += 0.1
        
        # 推荐情感加分
        if sentiment == "推荐":
            base += 0.05
        
        return min(base, 1.0)
    
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
    
    def to_dict_list(self) -> List[Dict]:
        """转换为字典列表"""
        return [asdict(poi) for poi in self.pois]


# ==================== 测试 ====================

def test_extractor():
    """测试广义 POI 提取器"""
    extractor = GeneralizedPOIExtractor()
    
    # 测试数据（包含非标准 POI）
    test_posts = [
        {
            "title": "发现一个绝美日落观赏点！在山顶右侧",
            "content": "徒步 30 分钟到达山顶，右侧有个观景台，是看日落的最佳机位。旁边有补给点可以买水和零食。山顶还有个洗手间，很方便。",
            "comments": [
                {"content": "请问观景台具体在哪？怎么过去？", "likes": 50},
                {"content": "补给点价格贵吗？", "likes": 25},
                {"content": "山顶的洗手间干净吗？", "likes": 18},
                {"content": "推荐去！旁边还有个拍照点，视野超好", "likes": 35},
            ],
            "likes": 1500,
            "comments_count": 128
        },
        {
            "title": "免费拍照点分享！人少景美",
            "content": "这个打卡点不用门票，也不用排队。在景区入口旁边，有个小亭子，是拍日出的绝佳位置。附近有停车场和充电桩。",
            "comments": [
                {"content": "停车场收费吗？", "likes": 30},
                {"content": "宠物友好吗？可以带狗吗？", "likes": 22},
            ],
            "likes": 2300,
            "comments_count": 95
        }
    ]
    
    print("="*70)
    print("🎯 广义 POI 提取器 v3.0 测试")
    print("="*70)
    
    pois = extractor.process_posts(test_posts)
    
    print(f"\n✅ 提取到 {len(pois)} 个 POI\n")
    
    # 分类统计
    categories = {}
    types = {}
    for poi in pois:
        cat = poi.poi_category
        typ = poi.poi_type
        categories[cat] = categories.get(cat, 0) + 1
        types[typ] = types.get(typ, 0) + 1
    
    print("📊 分类统计:")
    for cat, count in categories.items():
        print(f"  {cat}: {count}")
    
    print("\n📊 类型统计:")
    for typ, count in sorted(types.items(), key=lambda x: -x[1]):
        print(f"  {typ}: {count}")
    
    print("\n" + "="*70)
    print("📋 POI 详情")
    print("="*70)
    
    for i, poi in enumerate(pois, 1):
        print(f"\n{i}. {poi.poi_name}")
        print(f"   分类：{poi.poi_category} - {poi.poi_type}")
        print(f"   城市：{poi.city}")
        if poi.location_desc:
            print(f"   位置：{poi.location_desc}")
        if poi.function_desc:
            print(f"   功能：{poi.function_desc}")
        print(f"   情感：{poi.sentiment}")
        print(f"   意图：{poi.user_intent}")
        print(f"   热度：{poi.heat_score}")
        print(f"   置信度：{poi.confidence:.2f}")
        print(f"   来源：{poi.source_type}")
    
    # 保存结果
    output_file = f"xhs_lx/xhs_lx/poi_generalized_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(extractor.to_dict_list(), f, ensure_ascii=False, indent=2)
    
    print(f"\n💾 结果已保存：{output_file}")
    print("="*70)
    
    return pois


if __name__ == "__main__":
    test_extractor()
