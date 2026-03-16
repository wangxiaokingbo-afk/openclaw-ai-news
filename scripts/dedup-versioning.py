#!/usr/bin/env python3
"""
热点资讯去重与版本化工具
功能：
1. 生成内容指纹 (MD5)
2. 检查是否已推送
3. 生成带时间戳的版本化文件名
4. 更新已推送记录
"""

import hashlib
import json
import os
from datetime import datetime
from typing import List, Dict, Optional

CONFIG_DIR = os.path.dirname(os.path.abspath(__file__))
PUSHED_ITEMS_FILE = os.path.join(CONFIG_DIR, 'pushed-items.json')
MAX_RETENTION = 500  # 保留最近 500 条
SIMILARITY_THRESHOLD = 0.9  # 相似度阈值 90%


def generate_fingerprint(title: str, content: str) -> str:
    """生成内容指纹 (MD5)"""
    # 提取标题 + 前 50 字
    text = f"{title}:{content[:50]}"
    return hashlib.md5(text.encode('utf-8')).hexdigest()


def load_pushed_items() -> Dict:
    """加载已推送记录"""
    if not os.path.exists(PUSHED_ITEMS_FILE):
        return {
            "version": "1.0",
            "created_at": datetime.now().isoformat(),
            "items": [],
            "stats": {"total_pushed": 0}
        }
    
    with open(PUSHED_ITEMS_FILE, 'r', encoding='utf-8') as f:
        return json.load(f)


def save_pushed_items(data: Dict):
    """保存已推送记录"""
    # 清理过期记录 (保留最近 MAX_RETENTION 条)
    if len(data['items']) > MAX_RETENTION:
        data['items'] = data['items'][-MAX_RETENTION:]
    
    with open(PUSHED_ITEMS_FILE, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2, ensure_ascii=False)


def is_duplicate(fingerprint: str, items: List[Dict]) -> bool:
    """检查是否已推送"""
    return any(item['fingerprint'] == fingerprint for item in items)


def generate_versioned_filename(base_name: str, file_type: str = 'md') -> str:
    """生成带时间戳的版本化文件名"""
    timestamp = datetime.now().strftime('%Y-%m-%d-%H%M')
    return f"{base_name}-{timestamp}.{file_type}"


def generate_report_path(report_name: str, file_type: str = 'md') -> str:
    """生成报告完整路径 (按日期分级目录)"""
    now = datetime.now()
    year = now.strftime('%Y')
    month = now.strftime('%m')
    day = now.strftime('%d')
    filename = generate_versioned_filename(report_name, file_type)
    
    return os.path.join(
        'reports', year, month, day, filename
    )


def mark_as_pushed(title: str, category: str, fingerprint: str, report_id: str):
    """标记为已推送"""
    data = load_pushed_items()
    
    data['items'].append({
        'fingerprint': fingerprint,
        'title': title,
        'category': category,
        'pushed_at': datetime.now().isoformat(),
        'report_id': report_id
    })
    
    # 更新统计
    data['stats']['total_pushed'] = len(data['items'])
    data['stats']['last_push_at'] = data['items'][-1]['pushed_at']
    
    # 分类统计
    if 'categories' not in data['stats']:
        data['stats']['categories'] = {}
    
    cat = data['stats']['categories']
    cat[category] = cat.get(category, 0) + 1
    
    save_pushed_items(data)


def deduplicate_candidates(candidates: List[Dict], category: str) -> List[Dict]:
    """对候选资讯去重，返回未推送的资讯"""
    data = load_pushed_items()
    pushed = data['items']
    
    unique = []
    for item in candidates:
        fp = generate_fingerprint(item['title'], item['content'])
        if not is_duplicate(fp, pushed):
            item['fingerprint'] = fp
            unique.append(item)
    
    return unique


if __name__ == '__main__':
    # 测试
    print("热点资讯去重与版本化工具 v1.0")
    print(f"已推送记录文件：{PUSHED_ITEMS_FILE}")
    
    data = load_pushed_items()
    print(f"当前已推送：{len(data['items'])} 条")
    print(f"保留上限：{MAX_RETENTION} 条")
    
    # 测试指纹生成
    fp = generate_fingerprint("测试标题", "测试内容" * 10)
    print(f"测试指纹：{fp}")
    
    # 测试文件名生成
    filename = generate_versioned_filename("daily-top10")
    print(f"测试文件名：{filename}")
    
    # 测试路径生成
    path = generate_report_path("daily-top10")
    print(f"测试路径：{path}")
