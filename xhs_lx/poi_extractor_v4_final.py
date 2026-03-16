#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
广义 POI 提取器 v4.1 - 优化版主 POI 组合命名
输出 CSV 格式
"""

import re
import json
import csv
from typing import List, Dict
from dataclasses import dataclass, asdict, fields
from datetime import datetime
from pathlib import Path


@dataclass
class POI:
    poi_name: str
    poi_category: str = ""
    poi_type: str = ""
    main_poi: str = ""
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


class POIExtractor:
    """广义 POI 提取器 v4.1"""
    
    POI_TYPES = {
        "景点": ["景区", "景点", "公园", "乐园", "海滩", "海岛", "山", "湖", "海", "古镇", "古城", "寺庙"],
        "住宿": ["酒店", "民宿", "宾馆", "客栈", "度假村", "营地", "大本营"],
        "餐饮": ["餐厅", "餐馆", "咖啡馆", "小吃店"],
        "拍照点": ["打卡点", "拍照点", "机位", "观景台", "拍摄点", "取景地"],
        "功能点": ["补给点", "停车点", "露营点", "休息点", "售票处", "入口", "出口"],
        "设施点": ["洗手间", "充电桩", "加油站", "饮水处", "储物柜"],
        "观测点": ["日出观测点", "日落观赏点", "观星点", "眺望台"],
    }
    
    CITIES = ["北京", "上海", "广州", "深圳", "杭州", "成都", "重庆", "西安", "南京", "武汉", "三亚", "丽江", "大理", "厦门", "青岛", "新疆", "西藏", "云南", "四川", "香港", "南昌", "济州岛", "吉隆坡"]
    
    def __init__(self):
        self.pois = []
    
    def detect_city(self, text: str) -> str:
        for city in self.CITIES:
            if city in text:
                return city
        return "未知"
    
    def detect_poi_type(self, name: str) -> tuple:
        for poi_type, keywords in self.POI_TYPES.items():
            for keyword in keywords:
                if keyword in name:
                    return ("导航类", poi_type)
        return ("导航类", "其他")
    
    def extract_main_pois(self, text: str, city: str) -> List[str]:
        """提取主 POI（干净的地名）"""
        main_pois = []
        
        # 模式 1: 城市 + 后续地名（最多 15 字）
        if city in self.CITIES:
            idx = text.find(city)
            if idx >= 0:
                following = text[idx:idx+20]
                for sep in ['，', '。', ',', '.', '的', '去', '到', '在', '有', '从']:
                    if sep in following:
                        pos = following.find(sep)
                        if pos > 2:
                            following = following[:pos]
                            break
                if 4 <= len(following) <= 20:
                    main_pois.append(following)
        
        # 模式 2: 路线/古道/营地
        route_keywords = ["古道", "路线", "线路", "徒步线", "营地", "大本营"]
        for keyword in route_keywords:
            if keyword in text:
                idx = text.find(keyword)
                start = max(0, idx - 12)
                prefix = text[start:idx]
                # 清理前缀
                for sep in ['，', '。', ',', '.', ' ', '去', '到', '在', '从', '沿着']:
                    if sep in prefix:
                        prefix = prefix[prefix.rfind(sep)+len(sep):]
                name = prefix + keyword
                if 3 <= len(name) <= 20:
                    main_pois.append(name)
        
        return list(set(main_pois))
    
    def extract_functional_pois(self, text: str) -> List[str]:
        """提取功能型 POI"""
        pois = []
        
        functional_keywords = ["补给点", "停车点", "露营点", "拍照点", "打卡点", "机位", "观景台", "洗手间", "充电桩", "售票处", "入口", "出口", "日出观测点", "日落观赏点"]
        
        for keyword in functional_keywords:
            if keyword in text:
                pois.append(keyword)
        
        return list(set(pois))
    
    def combine_poi_names(self, text: str, city: str) -> List[Dict]:
        """组合主 POI + 功能点"""
        combined = []
        
        main_pois = self.extract_main_pois(text, city)
        functional_pois = self.extract_functional_pois(text)
        
        # 组合：主 POI + 功能点
        for func_poi in functional_pois:
            func_idx = text.find(func_poi)
            
            # 找最近的主 POI（前后 50 字内）
            best_main = None
            best_dist = 999
            
            for main_poi in main_pois:
                main_idx = text.find(main_poi)
                if main_idx >= 0:
                    dist = abs(func_idx - main_idx)
                    if dist < 50 and dist < best_dist:
                        best_dist = dist
                        best_main = main_poi
            
            if best_main:
                # 组合命名，避免重复
                if best_main.endswith(func_poi) or func_poi in best_main:
                    full_name = best_main
                else:
                    full_name = best_main + func_poi
                
                combined.append({
                    "name": full_name,
                    "main_poi": best_main,
                    "func_poi": func_poi,
                    "type": self.detect_poi_type(func_poi)[1]
                })
            else:
                combined.append({
                    "name": func_poi,
                    "main_poi": "",
                    "func_poi": func_poi,
                    "type": self.detect_poi_type(func_poi)[1]
                })
        
        # 添加主 POI（如果没有被组合）
        for main_poi in main_pois:
            is_combined = any(c["main_poi"] == main_poi for c in combined)
            if not is_combined:
                combined.append({
                    "name": main_poi,
                    "main_poi": main_poi,
                    "func_poi": "",
                    "type": self.detect_poi_type(main_poi)[1]
                })
        
        return combined
    
    def extract_from_post(self, post: Dict) -> List[POI]:
        """从帖子中提取 POI"""
        all_pois = []
        
        title = post.get("title", "")
        content = post.get("content", "")
        comments = post.get("comments", [])
        likes = post.get("likes", 0)
        comments_count = post.get("comments_count", 0)
        
        city = self.detect_city(f"{title} {content}")
        
        # 从标题提取
        if title:
            entities = self.combine_poi_names(title, city)
            for ent in entities:
                poi = POI(
                    poi_name=ent["name"],
                    main_poi=ent["main_poi"],
                    poi_type=ent["type"],
                    poi_category="导航类",
                    city=city,
                    heat_score=round(likes * 1.0 + comments_count * 5.0, 2),
                    source_text=title,
                    source_type="post_title",
                    confidence=0.85
                )
                all_pois.append(poi)
        
        # 从正文提取
        if content:
            entities = self.combine_poi_names(content, city)
            for ent in entities:
                poi = POI(
                    poi_name=ent["name"],
                    main_poi=ent["main_poi"],
                    poi_type=ent["type"],
                    poi_category="导航类",
                    city=city,
                    heat_score=round(likes * 1.0 + comments_count * 5.0, 2),
                    source_text=content[:100],
                    source_type="post_content",
                    confidence=0.70
                )
                all_pois.append(poi)
        
        # 从评论提取
        for comment in comments:
            comment_text = comment.get("content", "")
            comment_likes = comment.get("likes", 0)
            if comment_text:
                entities = self.combine_poi_names(comment_text, city)
                for ent in entities:
                    poi = POI(
                        poi_name=ent["name"],
                        main_poi=ent["main_poi"],
                        poi_type=ent["type"],
                        poi_category="导航类",
                        city=city,
                        heat_score=round(comment_likes * 1.0, 2),
                        source_text=comment_text[:100],
                        source_type="comment",
                        confidence=0.65
                    )
                    all_pois.append(poi)
        
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
        
        return list(unique.values())
    
    def to_csv(self, pois: List[POI], output_file: str):
        """导出 CSV"""
        if not pois:
            return
        
        fieldnames = [f.name for f in fields(POI)]
        
        with open(output_file, 'w', encoding='utf-8-sig', newline='') as f:
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            for poi in pois:
                writer.writerow(asdict(poi))


def main():
    """主流程"""
    print("="*70)
    print("🎯 广义 POI 提取 v4.1 - 生成 CSV")
    print("="*70)
    
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
        },
        {
            "title": "新疆伊犁那拉提草原露营攻略",
            "content": "那拉提草原景区内有专门的露营点，旁边有补给点可以买水。景区入口有停车场和洗手间。",
            "comments": [
                {"content": "那拉提草原露营点收费吗？", "likes": 30},
                {"content": "景区入口的停车场大吗？", "likes": 15},
            ],
            "likes": 2100,
            "comments_count": 95
        }
    ]
    
    extractor = POIExtractor()
    pois = extractor.process_posts(test_posts)
    
    print(f"\n✅ 提取到 {len(pois)} 个 POI\n")
    
    # 按主 POI 分组展示
    main_groups = {}
    for poi in pois:
        main = poi.main_poi if poi.main_poi else "(无主 POI)"
        if main not in main_groups:
            main_groups[main] = []
        main_groups[main].append(poi)
    
    print("📊 按主 POI 分组:")
    for main, group in main_groups.items():
        print(f"\n  【{main}】 ({len(group)}个)")
        for poi in group:
            print(f"    - {poi.poi_name} ({poi.poi_type})")
    
    # 导出 CSV
    output_dir = Path("xhs_lx/xhs_lx")
    output_dir.mkdir(exist_ok=True)
    
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    csv_file = output_dir / f"poi_generalized_{timestamp}.csv"
    json_file = output_dir / f"poi_generalized_{timestamp}.json"
    
    extractor.to_csv(pois, str(csv_file))
    
    # 也保存 JSON
    with open(json_file, 'w', encoding='utf-8') as f:
        json.dump([asdict(p) for p in pois], f, ensure_ascii=False, indent=2)
    
    print(f"\n💾 文件已保存:")
    print(f"   CSV: {csv_file}")
    print(f"   JSON: {json_file}")
    
    # 统计
    print(f"\n📊 统计:")
    print(f"   总 POI 数：{len(pois)}")
    
    type_counts = {}
    for poi in pois:
        t = poi.poi_type
        type_counts[t] = type_counts.get(t, 0) + 1
    
    for t, c in sorted(type_counts.items(), key=lambda x: -x[1]):
        print(f"   {t}: {c}个")
    
    print("="*70)
    
    return str(csv_file), str(json_file)


if __name__ == "__main__":
    main()
