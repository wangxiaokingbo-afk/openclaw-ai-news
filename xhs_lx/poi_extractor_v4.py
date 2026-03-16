#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
广义 POI 提取器 v4.0
支持主 POI + 功能点组合命名
例如："乌孙古道琼库什台河谷营地补给点"
"""

import re
import json
from typing import List, Dict
from dataclasses import dataclass, asdict
from datetime import datetime


@dataclass
class POI:
    """广义 POI 数据结构"""
    poi_name: str
    poi_category: str = ""
    poi_type: str = ""
    main_poi: str = ""  # 主 POI 名称（用于组合命名）
    city: str = ""
    province: str = ""
    location_desc: str = ""
    function_desc: str = ""
    sentiment: str = ""
    heat_score: float = 0.0
    source_text: str = ""
    source_type: str = ""
    confidence: float = 0.0
    user_intent: str = ""


class GeneralizedPOIExtractor:
    """
    广义 POI 提取器 v4.0
    
    核心特性：
    1. 主 POI + 功能点组合命名
    2. 识别路线/古道/营地等大地名
    3. 识别补给点/拍照点等功能点
    """
    
    # POI 类型库
    POI_TYPES = {
        "景点": ["景区", "景点", "公园", "乐园", "海滩", "海岛", "山", "湖", "海", "古镇", "古城"],
        "住宿": ["酒店", "民宿", "宾馆", "客栈", "度假村", "营地", "大本营"],
        "餐饮": ["餐厅", "餐馆", "咖啡馆", "小吃店"],
        "拍照点": ["打卡点", "拍照点", "机位", "观景台", "拍摄点", "取景地"],
        "功能点": ["补给点", "停车点", "露营点", "休息点", "售票处", "入口", "出口"],
        "设施点": ["洗手间", "充电桩", "加油站", "饮水处", "储物柜"],
        "观测点": ["日出观测点", "日落观赏点", "观星点", "眺望台"],
    }
    
    # 路线/古道关键词
    ROUTE_KEYWORDS = ["古道", "路线", "线路", "徒步线", "穿越线", "小径", "步道"]
    
    CITIES = ["北京", "上海", "广州", "深圳", "杭州", "成都", "重庆", "西安", "南京", "武汉", "三亚", "丽江", "大理", "厦门", "青岛", "新疆", "西藏", "云南", "四川"]
    
    def __init__(self):
        self.pois = []
    
    def detect_city(self, text: str) -> str:
        """检测城市"""
        for city in self.CITIES:
            if city in text:
                return city
        return "未知"
    
    def detect_poi_type(self, name: str) -> tuple:
        """检测 POI 类型"""
        for poi_type, keywords in self.POI_TYPES.items():
            for keyword in keywords:
                if keyword in name:
                    if poi_type in ["景点", "住宿", "餐饮"]:
                        return ("导航类", poi_type)
                    else:
                        return ("导航类", poi_type)
        return ("导航类", "其他")
    
    def extract_main_pois(self, text: str, city: str) -> List[Dict]:
        """
        提取主 POI（大地名、路线名、营地名）
        
        例如："乌孙古道"、"琼库什台河谷营地"
        """
        main_pois = []
        
        # 模式 1: 路线/古道名
        for keyword in self.ROUTE_KEYWORDS:
            if keyword in text:
                idx = text.find(keyword)
                # 往前找最多 10 字
                start = max(0, idx - 10)
                prefix = text[start:idx]
                # 清理前缀
                for sep in ['，', '。', ',', '.', ' ', '去', '到', '在', '从']:
                    if sep in prefix:
                        prefix = prefix[prefix.rfind(sep)+len(sep):]
                
                name = prefix + keyword
                if 2 <= len(name) <= 20:
                    main_pois.append({
                        "name": name,
                        "type": "功能点",
                        "category": "导航类"
                    })
        
        # 模式 2: 营地/大本营
        camp_keywords = ["营地", "大本营", "集结点", "落脚点"]
        for keyword in camp_keywords:
            if keyword in text:
                idx = text.find(keyword)
                start = max(0, idx - 12)
                prefix = text[start:idx]
                for sep in ['，', '。', ',', '.', ' ', '的']:
                    if sep in prefix:
                        prefix = prefix[prefix.rfind(sep)+len(sep):]
                
                name = prefix + keyword
                if 2 <= len(name) <= 25:
                    main_pois.append({
                        "name": name,
                        "type": "住宿",
                        "category": "导航类"
                    })
        
        # 模式 3: 城市/地名 + 后续
        if city in self.CITIES:
            idx = text.find(city)
            if idx >= 0:
                following = text[idx:idx+25]
                for sep in ['，', '。', ',', '.', '的']:
                    if sep in following:
                        pos = following.find(sep)
                        if pos > 2:
                            following = following[:pos]
                            break
                
                if 4 <= len(following) <= 25:
                    category, poi_type = self.detect_poi_type(following)
                    main_pois.append({
                        "name": following,
                        "type": poi_type,
                        "category": category
                    })
        
        return main_pois
    
    def extract_functional_pois(self, text: str) -> List[Dict]:
        """
        提取功能型 POI（补给点/拍照点/洗手间等）
        
        例如："补给点"、"拍照点"
        """
        pois = []
        
        functional_types = {
            "拍照点": ["打卡点", "拍照点", "机位", "观景台", "拍摄点"],
            "功能点": ["补给点", "停车点", "露营点", "休息点", "售票处"],
            "设施点": ["洗手间", "充电桩", "加油站", "饮水处"],
            "观测点": ["日出观测点", "日落观赏点", "观星点"],
        }
        
        for poi_type, keywords in functional_types.items():
            for keyword in keywords:
                if keyword in text:
                    idx = text.find(keyword)
                    start = max(0, idx - 10)
                    prefix = text[start:idx]
                    
                    for sep in ['，', '。', ',', '.', ' ', '有', '个']:
                        if sep in prefix:
                            prefix = prefix[prefix.rfind(sep)+len(sep):]
                            break
                    
                    name = prefix + keyword
                    if 2 <= len(name) <= 20:
                        pois.append({
                            "name": name,
                            "type": poi_type,
                            "category": "导航类"
                        })
        
        return pois
    
    def combine_poi_names(self, main_pois: List[Dict], functional_pois: List[Dict], text: str) -> List[Dict]:
        """
        组合主 POI + 功能点，形成完整命名
        
        例如：
        - 主 POI: "琼库什台河谷营地"
        - 功能点： "补给点"
        - 组合： "琼库什台河谷营地补给点"
        """
        combined = []
        
        for func_poi in functional_pois:
            func_idx = text.find(func_poi["name"])
            
            # 查找附近的主 POI（前后 50 字内）
            best_main_poi = None
            best_distance = 999
            
            for main_poi in main_pois:
                main_idx = text.find(main_poi["name"])
                if main_idx >= 0:
                    distance = abs(func_idx - main_idx)
                    if distance < 50 and distance < best_distance:
                        best_distance = distance
                        best_main_poi = main_poi
            
            # 组合命名
            if best_main_poi:
                full_name = best_main_poi["name"] + func_poi["name"]
                combined.append({
                    "name": full_name,
                    "type": func_poi["type"],
                    "category": func_poi["category"],
                    "main_poi": best_main_poi["name"]
                })
            else:
                # 没有主 POI，单独使用
                combined.append({
                    "name": func_poi["name"],
                    "type": func_poi["type"],
                    "category": func_poi["category"],
                    "main_poi": ""
                })
        
        # 添加主 POI（如果是标准类型）
        for main_poi in main_pois:
            if main_poi["type"] in ["景点", "住宿", "餐饮", "功能点"]:
                # 检查是否已被组合
                is_combined = any(c.get("main_poi") == main_poi["name"] for c in combined)
                if not is_combined:
                    combined.append(main_poi)
        
        return combined
    
    def extract_poi_name(self, text: str, city: str) -> List[Dict]:
        """提取 POI 名称（主流程）"""
        # 1. 提取主 POI
        main_pois = self.extract_main_pois(text, city)
        
        # 2. 提取功能点
        functional_pois = self.extract_functional_pois(text)
        
        # 3. 组合命名
        combined = self.combine_poi_names(main_pois, functional_pois, text)
        
        # 去重
        unique = []
        seen = set()
        for poi in combined:
            key = poi["name"]
            if key not in seen:
                seen.add(key)
                unique.append(poi)
        
        return unique
    
    def extract_from_text(self, text: str, source_type: str, likes: int = 0, comments: int = 0) -> List[POI]:
        """从文本中提取 POI"""
        pois = []
        city = self.detect_city(text)
        
        poi_entities = self.extract_poi_name(text, city)
        
        for entity in poi_entities:
            poi = POI(
                poi_name=entity["name"],
                poi_category=entity["category"],
                poi_type=entity["type"],
                main_poi=entity.get("main_poi", ""),
                city=city,
                heat_score=round(likes * 1.0 + comments * 5.0, 2),
                source_text=text[:100],
                source_type=source_type,
                confidence=0.8 if source_type == "post_title" else 0.6
            )
            pois.append(poi)
        
        return pois
    
    def extract_from_post(self, post: Dict) -> List[POI]:
        """从帖子中提取 POI（包括评论）"""
        all_pois = []
        
        # 标题
        title = post.get("title", "")
        if title:
            pois = self.extract_from_text(title, "post_title", post.get("likes", 0), post.get("comments_count", 0))
            all_pois.extend(pois)
        
        # 正文
        content = post.get("content", "")
        if content:
            pois = self.extract_from_text(content, "post_content", post.get("likes", 0), post.get("comments_count", 0))
            all_pois.extend(pois)
        
        # 评论
        comments = post.get("comments", [])
        for comment in comments:
            comment_text = comment.get("content", "")
            comment_likes = comment.get("likes", 0)
            if comment_text:
                pois = self.extract_from_text(comment_text, "comment", comment_likes, 0)
                all_pois.extend(pois)
        
        return all_pois
    
    def process_posts(self, posts: List[Dict]) -> List[POI]:
        """批量处理"""
        all_pois = []
        for post in posts:
            pois = self.extract_from_post(post)
            all_pois.extend(pois)
        
        # 去重
        unique = {}
        for poi in all_pois:
            key = f"{poi.poi_name}_{poi.city}"
            if key not in unique or poi.confidence > unique[key].confidence:
                unique[key] = poi
        
        self.pois = list(unique.values())
        return self.pois


# ==================== 测试 ====================

def test_v4():
    """测试 v4 版本"""
    extractor = GeneralizedPOIExtractor()
    
    # 测试数据
    test_posts = [
        {
            "title": "乌孙古道徒步攻略！琼库什台河谷营地补给点分享",
            "content": "从琼库什台村出发，沿着乌孙古道徒步 30 公里到达河谷营地。营地有个补给点可以买水和食物。旁边还有洗手间和充电桩。",
            "comments": [
                {"content": "请问琼库什台河谷营地补给点价格贵吗？", "likes": 50},
                {"content": "乌孙古道的机位在哪里？", "likes": 35},
                {"content": "营地旁边的洗手间干净吗？", "likes": 20},
            ],
            "likes": 3500,
            "comments_count": 180
        },
        {
            "title": "三亚亚龙湾日落观景台拍照点推荐",
            "content": "亚龙湾海滩有个绝佳的日落观赏点，在沙滩右侧。旁边有个拍照点，是拍日落的最佳机位。",
            "comments": [
                {"content": "亚龙湾海滩的拍照点具体在哪？", "likes": 40},
                {"content": "日落观赏点需要门票吗？", "likes": 25},
            ],
            "likes": 2800,
            "comments_count": 150
        }
    ]
    
    print("="*70)
    print("🎯 广义 POI 提取器 v4.0 - 主 POI 组合命名测试")
    print("="*70)
    
    pois = extractor.process_posts(test_posts)
    
    print(f"\n✅ 提取到 {len(pois)} 个 POI\n")
    
    # 按主 POI 分组
    main_poi_groups = {}
    for poi in pois:
        main = poi.main_poi if poi.main_poi else "(无主 POI)"
        if main not in main_poi_groups:
            main_poi_groups[main] = []
        main_poi_groups[main].append(poi)
    
    print("📊 按主 POI 分组:")
    for main, group in main_poi_groups.items():
        print(f"\n  【{main}】 ({len(group)}个)")
        for poi in group:
            print(f"    - {poi.poi_name} ({poi.poi_type})")
    
    print("\n" + "="*70)
    print("📋 POI 详情")
    print("="*70)
    
    for i, poi in enumerate(pois, 1):
        print(f"\n{i}. {poi.poi_name}")
        if poi.main_poi:
            print(f"   主 POI: {poi.main_poi}")
        print(f"   类型：{poi.poi_type}")
        print(f"   城市：{poi.city}")
        print(f"   热度：{poi.heat_score}")
        print(f"   置信度：{poi.confidence:.2f}")
        print(f"   来源：{poi.source_type}")
    
    # 保存
    output_file = f"xhs_lx/xhs_lx/poi_v4_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump([asdict(p) for p in pois], f, ensure_ascii=False, indent=2)
    
    print(f"\n💾 结果已保存：{output_file}")
    print("="*70)


if __name__ == "__main__":
    test_v4()
