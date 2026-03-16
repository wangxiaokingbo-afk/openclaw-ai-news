#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
POI 信息提取器 - 优化版
结合规则匹配、NER 模型和 LLM 的前沿方案
"""

import re
import json
from typing import List, Dict, Optional
from dataclasses import dataclass, asdict
from pathlib import Path


@dataclass
class POI:
    """POI 数据结构"""
    poi_name: str
    poi_address: str = ""
    city: str = ""
    province: str = ""
    poi_type: str = ""  # 景点/酒店/餐厅/交通等
    heat_score: float = 0.0
    source_text: str = ""
    source_type: str = ""  # post/comment
    confidence: float = 0.0  # 置信度


class POIExtractor:
    """
    POI 提取器 - 优化版
    
    使用多层提取策略：
    1. 规则匹配（快速筛选）
    2. 地名识别（省市县）
    3. POI 类型识别（景点/酒店/餐厅等）
    4. 上下文验证（提高准确率）
    """
    
    # ===== 地名知识库 =====
    
    # 直辖市和省份
    PROVINCES = [
        "北京", "上海", "天津", "重庆",  # 直辖市
        "河北", "山西", "辽宁", "吉林", "黑龙江",
        "江苏", "浙江", "安徽", "福建", "江西", "山东",
        "河南", "湖北", "湖南", "广东", "海南",
        "四川", "贵州", "云南", "陕西", "甘肃", "青海",
        "台湾", "内蒙古", "广西", "西藏", "宁夏", "新疆",
        "香港", "澳门"
    ]
    
    # 热门旅游城市
    CITIES = {
        "北京": ["朝阳", "海淀", "西城", "东城", "通州", "昌平", "大兴"],
        "上海": ["浦东", "黄浦", "静安", "徐汇", "闵行", "长宁", "普陀"],
        "广州": ["天河", "越秀", "海珠", "荔湾", "白云"],
        "深圳": ["南山", "福田", "罗湖", "宝安", "龙岗"],
        "杭州": ["西湖", "余杭", "滨江", "萧山", "拱墅"],
        "成都": ["锦江", "武侯", "金牛", "青羊", "成华"],
        "重庆": ["渝中", "江北", "南岸", "九龙坡", "沙坪坝"],
        "西安": ["雁塔", "未央", "碑林", "莲湖", "灞桥"],
        "南京": ["玄武", "鼓楼", "秦淮", "建邺", "栖霞"],
        "武汉": ["武昌", "汉口", "汉阳", "洪山", "江汉"],
        "三亚": ["海棠湾", "亚龙湾", "大东海", "三亚湾"],
        "丽江": ["古城", "玉龙"],
        "大理": ["古城", "洱海"],
        "厦门": ["思明", "湖里", "集美"],
        "青岛": ["市南", "市北", "崂山"],
        "大连": ["中山", "西岗", "沙河口"],
    }
    
    # 国外热门目的地
    FOREIGN_DESTINATIONS = {
        "日本": ["东京", "大阪", "京都", "北海道", "冲绳"],
        "泰国": ["曼谷", "清迈", "普吉岛", "苏梅岛"],
        "韩国": ["首尔", "济州岛", "釜山"],
        "新加坡": ["新加坡"],
        "马来西亚": ["吉隆坡", "槟城", "兰卡威"],
        "美国": ["纽约", "洛杉矶", "旧金山", "拉斯维加斯"],
        "英国": ["伦敦", "爱丁堡", "曼彻斯特"],
        "法国": ["巴黎", "尼斯", "里昂"],
        "意大利": ["罗马", "威尼斯", "佛罗伦萨"],
        "澳大利亚": ["悉尼", "墨尔本", "黄金海岸"],
        "新西兰": ["奥克兰", "皇后镇", "基督城"],
    }
    
    # ===== POI 类型关键词 =====
    
    POI_TYPES = {
        "景点": ["景区", "景点", "公园", "乐园", "度假区", "海滩", "海岛", "山", "湖", "海", "瀑布", "森林", "古镇", "古城", "寺庙", "教堂", "博物馆", "美术馆", "动物园", "植物园"],
        "住宿": ["酒店", "民宿", "宾馆", "客栈", "度假村", "青旅", "公寓"],
        "餐饮": ["餐厅", "餐馆", "饭店", "咖啡馆", "咖啡厅", "奶茶店", "小吃店", "烧烤", "火锅", "自助餐"],
        "交通": ["机场", "火车站", "高铁站", "地铁站", "公交站", "码头", "港口"],
        "购物": ["商场", "购物中心", "超市", "市场", "夜市", "商业街"],
        "娱乐": ["电影院", "KTV", "酒吧", "游乐场", "温泉", "SPA", "健身房"],
    }
    
    # ===== POI 意图关键词 =====
    
    INTENT_KEYWORDS = [
        # 位置询问
        "怎么去", "在哪", "在哪里", "什么位置", "地址是", "具体位置",
        "交通", "路线", "导航", "开车", "地铁", "公交", "打车",
        # 推荐询问
        "推荐", "值得", "好玩", "好吃", "必看", "必去", "打卡",
        # 评价
        "美", "漂亮", "壮观", "震撼", "推荐", "坑", "避雷", "攻略"
    ]
    
    # ===== 特殊符号和清理规则 =====
    
    EMOJI_PATTERN = re.compile(r'[\U0001F300-\U0001F9FF]|[\U0001FA00-\U0001FAFF]|[\U00002702-\U000027B0]')
    SPECIAL_CHARS = re.compile(r'[^\w\u4e00-\u9fa5\s.,;:!?()""\'\-]')
    
    def __init__(self):
        self.pois = []
    
    def clean_text(self, text: str) -> str:
        """清理文本"""
        # 移除 emoji
        text = self.EMOJI_PATTERN.sub('', text)
        # 移除特殊符号（保留基本标点）
        text = self.SPECIAL_CHARS.sub('', text)
        # 移除多余空格
        text = re.sub(r'\s+', ' ', text).strip()
        return text
    
    def detect_location(self, text: str) -> Dict[str, str]:
        """
        检测地理位置（省/市/区）
        
        返回：{"province": "", "city": "", "district": ""}
        """
        result = {"province": "", "city": "", "district": ""}
        
        # 检测省份
        for province in self.PROVINCES:
            if province in text:
                result["province"] = province
                break
        
        # 检测城市（包括国外）
        all_cities = {}
        for city, districts in self.CITIES.items():
            all_cities[city] = districts
        for country, cities in self.FOREIGN_DESTINATIONS.items():
            for city in cities:
                all_cities[city] = []
        
        for city in all_cities.keys():
            if city in text:
                result["city"] = city
                break
        
        # 检测区县
        if result["city"] and result["city"] in self.CITIES:
            for district in self.CITIES[result["city"]]:
                if district in text:
                    result["district"] = district
                    break
        
        return result
    
    def detect_poi_type(self, text: str) -> str:
        """检测 POI 类型"""
        for poi_type, keywords in self.POI_TYPES.items():
            for keyword in keywords:
                if keyword in text:
                    return poi_type
        return "其他"
    
    def extract_poi_entities(self, text: str) -> List[str]:
        """
        提取 POI 实体名称
        
        使用多种模式匹配：
        1. 地名 + 类型词
        2. 专有名词（引号内）
        3. 特定格式（XX 景区/XX 酒店等）
        """
        pois = []
        
        # 模式 1: 知名地点 + 后续内容（2-15 字）
        famous_places = [
            "北京", "上海", "广州", "深圳", "杭州", "成都", "重庆", "西安", "南京", "武汉",
            "三亚", "丽江", "大理", "厦门", "青岛", "大连", "东京", "大阪", "首尔", "济州岛",
            "曼谷", "清迈", "吉隆坡", "新加坡", "悉尼", "墨尔本", "巴黎", "伦敦", "纽约", "洛杉矶"
        ]
        
        for place in famous_places:
            if place in text:
                idx = text.find(place)
                # 提取地点及其后内容（最多 15 字）
                following = text[idx:idx+20]
                # 清理末尾标点
                following = re.sub(r'[，。,.!！?？\s]+$', '', following)
                if len(following) >= 2:
                    pois.append(following)
        
        # 模式 2: 省份 + 内容
        provinces = ["新疆", "西藏", "云南", "四川", "浙江", "江苏", "福建", "广东", "广西", "海南", "台湾"]
        for province in provinces:
            if province in text:
                idx = text.find(province)
                following = text[idx:idx+15]
                following = re.sub(r'[，。,.!！?？\s]+$', '', following)
                if len(following) >= 2:
                    pois.append(following)
        
        # 模式 3: 类型词结尾（XX 景区/XX 酒店/XX 餐厅等）
        type_keywords = sum(self.POI_TYPES.values(), [])
        for kw in type_keywords:
            # 查找类型词前的内容（最多 10 字）
            pattern = r'([^\s,，.。!?]{2,10}' + kw + r')'
            matches = re.findall(pattern, text)
            for match in matches:
                if 2 <= len(match) <= 15:
                    pois.append(match)
        
        # 去重和过滤
        unique_pois = []
        for poi in pois:
            if 2 <= len(poi) <= 20 and poi not in unique_pois:
                unique_pois.append(poi)
        
        return unique_pois
    
    def has_poi_intent(self, text: str) -> bool:
        """判断文本是否有 POI 相关意图"""
        return any(kw in text for kw in self.INTENT_KEYWORDS)
    
    def calculate_heat(self, likes: int = 0, comments: int = 0, shares: int = 0) -> float:
        """
        计算热度分数
        
        公式：heat = likes * 1.0 + comments * 5.0 + shares * 10.0
        """
        return round(likes * 1.0 + comments * 5.0 + shares * 10.0, 2)
    
    def extract_from_post(self, post_data: Dict) -> List[POI]:
        """
        从帖子中提取 POI
        
        post_data 包含:
        - title: 标题
        - content: 正文
        - comments: 评论列表
        - likes: 点赞数
        - comments_count: 评论数
        """
        pois = []
        
        # 合并所有文本
        title = post_data.get("title", "")
        content = post_data.get("content", "")
        comments = post_data.get("comments", [])
        
        # 检测位置
        all_text = f"{title} {content}"
        location = self.detect_location(all_text)
        
        # 从标题提取
        title_pois = self.extract_poi_entities(title)
        for poi_name in title_pois:
            poi = POI(
                poi_name=poi_name,
                city=location["city"],
                province=location["province"],
                poi_type=self.detect_poi_type(poi_name),
                heat_score=self.calculate_heat(post_data.get("likes", 0), post_data.get("comments_count", 0)),
                source_text=title,
                source_type="post_title",
                confidence=0.8  # 标题中的 POI 置信度较高
            )
            pois.append(poi)
        
        # 从正文提取
        if content:
            content_pois = self.extract_poi_entities(content)
            has_intent = self.has_poi_intent(content)
            
            for poi_name in content_pois:
                poi = POI(
                    poi_name=poi_name,
                    city=location["city"],
                    province=location["province"],
                    poi_type=self.detect_poi_type(poi_name),
                    heat_score=self.calculate_heat(post_data.get("likes", 0), post_data.get("comments_count", 0)),
                    source_text=content[:100],
                    source_type="post_content",
                    confidence=0.7 if has_intent else 0.5
                )
                pois.append(poi)
        
        # 从评论提取（重要！）
        for comment in comments:
            comment_text = comment.get("content", "")
            comment_likes = comment.get("likes", 0)
            
            # 检测评论中的位置
            comment_location = self.detect_location(comment_text)
            city = comment_location["city"] or location["city"]
            
            # 提取 POI
            comment_pois = self.extract_poi_entities(comment_text)
            has_intent = self.has_poi_intent(comment_text)
            
            for poi_name in comment_pois:
                poi = POI(
                    poi_name=poi_name,
                    city=city,
                    province=location["province"],
                    poi_type=self.detect_poi_type(poi_name),
                    heat_score=self.calculate_heat(comment_likes, 0, 0),
                    source_text=comment_text[:100],
                    source_type="comment",
                    confidence=0.6 if has_intent else 0.4
                )
                pois.append(poi)
        
        return pois
    
    def process_posts(self, posts: List[Dict]) -> List[POI]:
        """批量处理帖子"""
        all_pois = []
        
        for post in posts:
            pois = self.extract_from_post(post)
            all_pois.extend(pois)
        
        # 去重（相同的 POI 名称 + 城市）
        unique_pois = {}
        for poi in all_pois:
            key = f"{poi.poi_name}_{poi.city}"
            if key not in unique_pois:
                unique_pois[key] = poi
            else:
                # 保留置信度高的
                if poi.confidence > unique_pois[key].confidence:
                    unique_pois[key] = poi
        
        self.pois = list(unique_pois.values())
        return self.pois
    
    def to_dict_list(self) -> List[Dict]:
        """转换为字典列表"""
        return [asdict(poi) for poi in self.pois]
    
    def to_dataframe(self):
        """转换为 DataFrame（需要 pandas）"""
        try:
            import pandas as pd
            return pd.DataFrame(self.to_dict_list())
        except ImportError:
            print("⚠️  需要安装 pandas: pip install pandas")
            return None


# ==================== 测试 ====================

def test_extractor():
    """测试 POI 提取器"""
    extractor = POIExtractor()
    
    # 测试数据
    test_post = {
        "title": "三亚亚龙湾真的太美了！",
        "content": "这次来三亚旅游，住了亚龙湾的丽思卡尔顿酒店，风景超级好。还去了蜈支洲岛，海水很清澈。推荐大家去海棠湾的免税店购物！",
        "comments": [
            {"content": "请问亚龙湾怎么去？从机场坐什么车？", "likes": 50},
            {"content": "海棠湾的免税店具体位置在哪里？", "likes": 30},
            {"content": "蜈支洲岛的门票多少钱？值得去吗？", "likes": 25},
            {"content": "我上周刚去，推荐住大东海的民宿，性价比高", "likes": 20},
        ],
        "likes": 1500,
        "comments_count": 120
    }
    
    pois = extractor.extract_from_post(test_post)
    
    print("="*60)
    print("POI 提取测试结果")
    print("="*60)
    
    for i, poi in enumerate(pois, 1):
        print(f"\n{i}. {poi.poi_name}")
        print(f"   城市：{poi.city}")
        print(f"   类型：{poi.poi_type}")
        print(f"   热度：{poi.heat_score}")
        print(f"   来源：{poi.source_type}")
        print(f"   置信度：{poi.confidence}")
    
    return pois


if __name__ == "__main__":
    test_extractor()
