#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
小红书旅行数据抓取 + POI 提取 + 高德验证 全流程脚本
"""

import json
import os
import re
from datetime import datetime
from pathlib import Path
import time

# ==================== 第一步：抓取小红书数据 ====================

class XiaohongshuScraper:
    """小红书数据抓取器"""
    
    def __init__(self, output_dir="xhs_lx"):
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(exist_ok=True)
    
    def generate_filename(self):
        """生成时间戳文件名"""
        return datetime.now().strftime("%Y%m%d_%H%M%S") + ".json"
    
    def scrape_travel_posts(self, browser_tool, target_id):
        """
        抓取旅行频道帖子数据
        
        参数:
            browser_tool: 浏览器工具实例
            target_id: 标签页 ID
        
        返回:
            帖子数据列表
        """
        posts_data = []
        
        # 这里需要通过浏览器工具获取页面数据
        # 由于是演示，我们模拟数据结构
        # 实际使用时需要调用 browser snapshot 并解析
        
        print("📸 正在抓取小红书旅行频道数据...")
        
        # 模拟数据结构（实际需要从浏览器 snapshot 解析）
        sample_post = {
            "title": "示例帖子标题",
            "content": "帖子正文内容...",
            "author": {
                "name": "作者名",
                "ip_location": "IP 属地"
            },
            "link": "https://www.xiaohongshu.com/explore/xxx",
            "likes": 1000,
            "comments_count": 50,
            "comments": [
                {
                    "content": "评论内容",
                    "likes": 10,
                    "sub_comments": []
                }
            ],
            "crawl_time": datetime.now().isoformat()
        }
        
        posts_data.append(sample_post)
        
        return posts_data
    
    def save_to_json(self, data):
        """保存数据到 JSON 文件"""
        filename = self.generate_filename()
        filepath = self.output_dir / filename
        
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        
        print(f"✅ 数据已保存：{filepath}")
        return filepath


# ==================== 第二步：POI 信息提取 ====================

class POIExtractor:
    """POI 信息提取器"""
    
    # POI 相关关键词
    POI_KEYWORDS = [
        "怎么去", "在哪", "在哪里", "位置", "地址", "交通",
        "地铁", "公交", "开车", "导航", "路线", "到达",
        "靠近", "旁边", "附近", "对面", "路口", "站",
        "景区", "景点", "酒店", "民宿", "餐厅", "咖啡馆",
        "打卡", "拍照", "推荐", "好玩", "值得"
    ]
    
    # 城市关键词映射（简化版）
    CITY_KEYWORDS = {
        "北京": ["北京", "朝阳", "海淀", "西城", "东城"],
        "上海": ["上海", "浦东", "黄浦", "静安", "徐汇"],
        "广州": ["广州", "天河", "越秀", "海珠"],
        "深圳": ["深圳", "南山", "福田", "罗湖"],
        "杭州": ["杭州", "西湖", "余杭", "滨江"],
        "成都": ["成都", "锦江", "武侯", "金牛"],
        "重庆": ["重庆", "渝中", "江北", "南岸"],
        "西安": ["西安", "雁塔", "未央", "碑林"],
        "南京": ["南京", "玄武", "鼓楼", "秦淮"],
        "武汉": ["武汉", "武昌", "汉口", "汉阳"],
    }
    
    def __init__(self):
        self.poi_data = []
    
    def extract_poi_from_text(self, text, post_info):
        """从文本中提取 POI 信息"""
        pois = []
        
        # 检查是否包含 POI 相关关键词
        has_poi_keyword = any(kw in text for kw in self.POI_KEYWORDS)
        
        if not has_poi_keyword:
            return pois
        
        # 提取疑似 POI 名称（简化：提取引号内或特定格式的内容）
        poi_patterns = [
            r'["「](.+?)["」]',  # 引号内的内容
            r'([^\s]{2,10}[景区景点酒店民宿餐厅咖啡馆])',  # 地点类型
        ]
        
        for pattern in poi_patterns:
            matches = re.findall(pattern, text)
            for match in matches:
                poi_name = match.strip()
                if len(poi_name) >= 2 and len(poi_name) <= 20:
                    # 识别城市
                    city = self.detect_city(text)
                    
                    # 计算热度
                    heat = self.calculate_heat(post_info)
                    
                    pois.append({
                        "poi_name": poi_name,
                        "poi_address": "",  # 待填充
                        "city": city,
                        "heat": heat,
                        "source_text": text[:100],  # 来源文本片段
                        "source_type": "post" if post_info.get("is_post") else "comment"
                    })
        
        return pois
    
    def detect_city(self, text):
        """检测文本中的城市"""
        for city, keywords in self.CITY_KEYWORDS.items():
            for keyword in keywords:
                if keyword in text:
                    return city
        return "未知"
    
    def calculate_heat(self, post_info):
        """计算热度值"""
        likes = post_info.get("likes", 0)
        comments = post_info.get("comments_count", 0)
        # 简单加权计算
        heat = likes * 1.0 + comments * 5.0
        return round(heat, 2)
    
    def process_json_file(self, json_filepath):
        """处理 JSON 文件，提取 POI"""
        print("🔍 正在解析 JSON 文件，提取 POI 信息...")
        
        with open(json_filepath, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        all_pois = []
        
        # 处理每个帖子
        if isinstance(data, list):
            for post in data:
                # 检查帖子正文
                post_info = {
                    "likes": post.get("likes", 0),
                    "comments_count": post.get("comments_count", 0),
                    "is_post": True
                }
                
                # 从标题提取
                title = post.get("title", "")
                pois = self.extract_poi_from_text(title, post_info)
                all_pois.extend(pois)
                
                # 从正文提取
                content = post.get("content", "")
                pois = self.extract_poi_from_text(content, post_info)
                all_pois.extend(pois)
                
                # 从评论提取
                comments = post.get("comments", [])
                for comment in comments:
                    comment_info = {
                        "likes": comment.get("likes", 0),
                        "comments_count": 0,
                        "is_post": False
                    }
                    pois = self.extract_poi_from_text(
                        comment.get("content", ""), 
                        comment_info
                    )
                    all_pois.extend(pois)
        
        self.poi_data = all_pois
        print(f"✅ 提取到 {len(all_pois)} 个疑似 POI")
        
        return all_pois


# ==================== 第三步：高德地图验证 ====================

class AMapVerifier:
    """高德地图 POI 验证器"""
    
    def __init__(self):
        self.results = []
    
    def clean_poi_name(self, name):
        """清理 POI 名称中的特殊字符"""
        # 移除特殊字符
        cleaned = re.sub(r'[^\w\u4e00-\u9fa5\s]', '', name)
        # 移除多余空格
        cleaned = re.sub(r'\s+', ' ', cleaned).strip()
        return cleaned
    
    def search_amap(self, city, poi_name):
        """
        搜索高德地图
        
        实际使用时需要调用高德 API 或浏览器自动化
        这里模拟验证逻辑
        """
        # 清理名称
        clean_name = self.clean_poi_name(poi_name)
        
        # 模拟搜索结果（实际需要通过高德 API 或浏览器）
        # 简单规则：名称长度>2 且不是"未知"城市，认为存在
        if len(clean_name) > 2 and city != "未知":
            # 模拟相似度检查
            similarity = 0.8  # 模拟 80% 相似
            exists = similarity > 0.5
            return {
                "exists": exists,
                "matched_name": clean_name if exists else None,
                "similarity": similarity
            }
        
        return {
            "exists": False,
            "matched_name": None,
            "similarity": 0
        }
    
    def verify_pois(self, pois):
        """验证 POI 列表"""
        print("🗺️ 正在通过高德地图验证 POI...")
        
        results = []
        
        for poi in pois:
            city = poi.get("city", "未知")
            name = poi.get("poi_name", "")
            
            # 搜索高德
            search_result = self.search_amap(city, name)
            
            result = {
                "poi_name": name,
                "poi_address": poi.get("poi_address", ""),
                "city": city,
                "heat": poi.get("heat", 0),
                "exists": "存在" if search_result["exists"] else "缺失",
                "matched_name": search_result.get("matched_name", ""),
                "similarity": search_result.get("similarity", 0)
            }
            
            results.append(result)
        
        self.results = results
        print(f"✅ 验证完成，共 {len(results)} 个 POI")
        
        return results
    
    def output_table(self, results=None):
        """输出 AI 表格格式"""
        if results is None:
            results = self.results
        
        # 输出 Markdown 表格
        print("\n" + "="*80)
        print("📊 POI 验证结果表格")
        print("="*80 + "\n")
        
        # 表头
        print("| 疑似 POI 名称 | 疑似 POI 地址 | 城市 | 热度 | 存在/缺失 |")
        print("|--------------|--------------|------|------|----------|")
        
        # 数据行
        for r in results:
            print(f"| {r['poi_name'][:20]} | {r['poi_address'][:15]} | {r['city']} | {r['heat']} | {r['exists']} |")
        
        print("\n" + "="*80)
        
        return results


# ==================== 主流程 ====================

def main():
    """主执行流程"""
    print("🚀 开始执行小红书数据获取和处理全流程...\n")
    
    # 第一步：抓取数据
    print("【第一步】抓取小红书旅行频道数据")
    print("-" * 50)
    scraper = XiaohongshuScraper()
    
    # 模拟抓取数据（实际需要通过浏览器工具）
    sample_data = [
        {
            "title": "2026 必去的 10 个旅行地📍",
            "content": "第一个推荐的是杭州西湖，真的太美了！怎么去？地铁 1 号线到龙翔桥站。位置在杭州市中心，交通很方便。",
            "author": {"name": "旅行达人", "ip_location": "浙江"},
            "link": "https://www.xiaohongshu.com/explore/abc123",
            "likes": 15420,
            "comments_count": 328,
            "comments": [
                {"content": "请问具体在哪？求地址！", "likes": 45, "sub_comments": []},
                {"content": "杭州西湖景区，靠近断桥那边", "likes": 23, "sub_comments": []},
                {"content": "交通方便吗？", "likes": 12, "sub_comments": []}
            ],
            "crawl_time": datetime.now().isoformat()
        },
        {
            "title": "成都这家火锅店绝了🔥",
            "content": "位置在春熙路附近，具体地址是锦江区 XX 路 XX 号。怎么去？地铁 2 号线春熙路站。",
            "author": {"name": "吃货小王", "ip_location": "四川"},
            "link": "https://www.xiaohongshu.com/explore/def456",
            "likes": 8930,
            "comments_count": 156,
            "comments": [
                {"content": "求具体位置", "likes": 30, "sub_comments": []},
                {"content": "这家餐厅值得打卡！", "likes": 18, "sub_comments": []}
            ],
            "crawl_time": datetime.now().isoformat()
        }
    ]
    
    json_filepath = scraper.save_to_json(sample_data)
    print()
    
    # 第二步：提取 POI
    print("【第二步】解析 JSON，提取 POI 信息")
    print("-" * 50)
    extractor = POIExtractor()
    pois = extractor.process_json_file(json_filepath)
    print()
    
    # 第三步：高德验证
    print("【第三步】高德地图验证 POI")
    print("-" * 50)
    verifier = AMapVerifier()
    results = verifier.verify_pois(pois)
    
    # 输出表格
    table_results = verifier.output_table()
    
    # 保存最终结果
    output_file = scraper.output_dir / "poi_verification_result.json"
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(table_results, f, ensure_ascii=False, indent=2)
    
    print(f"\n✅ 最终结果已保存：{output_file}")
    print("\n🎉 全流程执行完成！")
    
    return {
        "raw_data_file": str(json_filepath),
        "poi_count": len(pois),
        "verified_count": len(results),
        "output_file": str(output_file)
    }


if __name__ == "__main__":
    result = main()
    print("\n📋 执行摘要:")
    print(json.dumps(result, indent=2, ensure_ascii=False))
