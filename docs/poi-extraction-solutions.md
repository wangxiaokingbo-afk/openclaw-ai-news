# POI 地点提取能力对比

_最后更新：2026-03-15 01:50_

---

## 快速结论

| 方案 | 类型 | 传统 POI | 非典型 POI | 文本提取 | 成本 | 推荐度 |
|------|------|---------|-----------|---------|------|--------|
| **高德地图 API** | 地图 API | ⭐⭐⭐⭐⭐ | ⭐⭐ | ❌ | 免费额度 | 🟢 最佳 |
| **Google Places** | 地图 API | ⭐⭐⭐⭐⭐ | ⭐⭐⭐ | ❌ | $200 免费/月 | 🟢 最佳 |
| **Foursquare** | 地图 API | ⭐⭐⭐⭐ | ⭐⭐⭐⭐ | ❌ | $200 免费 | 🟢 推荐 |
| **POI 文本提取** | NLP 技能 | ⭐⭐ | ⭐⭐⭐⭐⭐ | ✅ | 免费 | 🟢 已有 |
| **Mapbox** | 地图 API | ⭐⭐⭐⭐ | ⭐⭐⭐ | ❌ | 免费额度 | 🟡 备选 |

---

## 方案一：高德地图 API（国内最佳）

**文档**：https://lbs.amap.com/api/webservice/guide/api/search

### 核心能力

| 功能 | 说明 |
|------|------|
| **关键字搜索** | 通过 POI 名称/类型搜索（如"肯德基"、"朝阳公园"） |
| **周边搜索** | 在经纬度附近搜索（半径 0-50km） |
| **多边形搜索** | 在自定义区域内搜索 |
| **ID 查询** | 通过 POI ID 查详情 |

### 返回数据

```json
{
  "pois": [{
    "id": "唯一 ID",
    "name": "名称",
    "type": "兴趣点类型",
    "address": "地址",
    "location": "经纬度",
    "tel": "电话",
    "rating": "评分",
    "cost": "人均消费",
    "photos": ["图片 URL"]
  }]
}
```

### POI 分类（部分）

| 大类 | 中类示例 | 代码 |
|------|---------|------|
| 汽车服务 | 加油站、租车 | 010000 |
| 餐饮服务 | 中餐厅、快餐 | 050000 |
| 购物服务 | 商场、超市 | 060000 |
| 生活服务 | 银行、医院 | 070000 |
| 体育休闲 | 健身房、KTV | 080000 |
| 医疗保健 | 医院、诊所 | 090000 |
| 住宿服务 | 酒店、民宿 | 100000 |
| 风景名胜 | 景点、公园 | 110000 |
| 商务住宅 | 写字楼、小区 | 120000 |
| 政府机构 | 政府、社团 | 130000 |
| 科教文化 | 学校、博物馆 | 140000 |
| 交通设施 | 机场、车站 | 150000 |

### 使用限制

| 项目 | 限制 |
|------|------|
| 日配额 | 免费版 5000 次/日 |
| QPS | 10 次/秒 |
| 翻页 | 最多 200 条（20 条×10 页） |

### 价格

- **免费版**：5000 次/日（够用）
- **企业版**：联系商务

---

## 方案二：Google Places API（国际最佳）

**文档**：https://developers.google.com/maps/documentation/places

### 核心能力

| 功能 | 说明 |
|------|------|
| **Place Search** | 文本搜索、附近搜索 |
| **Place Details** | 详细信息（评论、照片） |
| **Place Photos** | 高清照片 |
| **Autocomplete** | 自动补全 |

### 返回数据

```json
{
  "results": [{
    "place_id": "唯一 ID",
    "name": "名称",
    "types": ["类型数组"],
    "formatted_address": "地址",
    "geometry": {"location": {"lat": 0, "lng": 0}},
    "rating": 4.5,
    "user_ratings_total": 1234,
    "photos": [{"photo_reference": "xxx"}]
  }]
}
```

### 价格

| 项目 | 免费额度 | 超出价格 |
|------|---------|---------|
| Places API | $200/月 | $17/1000 次 |
| 估算调用 | 约 10000 次/月免费 |

---

## 方案三：Foursquare Places API（特色推荐）

**文档**：https://foursquare.com/developer

### 核心优势

| 特性 | 说明 |
|------|------|
| **非典型 POI** | 支持网红打卡点、小众地点 |
| **Taste 标签** | 用户自定义标签（如"适合拍照"） |
| **Tips** | 用户真实评价 |
| **Trending** | 实时热门地点 |

### 价格

- **免费**：$200 信用点/月
- **商用**：联系商务

---

## 方案四：已有 POI 文本提取技能

**路径**：`~/.openclaw/workspace/skills/poi-extractor/`

### 核心能力

| 功能 | 说明 |
|------|------|
| **规则匹配** | 基于地名知识库 +POI 类型词 |
| **省市识别** | 支持国内城市 + 国外热门目的地 |
| **POI 类型** | 景点/住宿/餐饮/交通/购物/娱乐 |
| **置信度** | 0.4-0.8 分级 |
| **热度计算** | 基于点赞/评论数 |

### 支持的地名

**国内**：
- 4 个直辖市 + 23 个省
- 15+ 热门旅游城市（北京、上海、三亚、丽江等）

**国外**：
- 日本、泰国、韩国、新加坡、马来西亚
- 美国、英国、法国、意大利
- 澳大利亚、新西兰

### 提取示例

**输入**：
```
三亚亚龙湾真的太美了！住了亚龙湾的丽思卡尔顿酒店，
还去了蜈支洲岛。推荐去海棠湾的免税店购物！
```

**输出**：
```json
[
  {
    "poi_name": "三亚亚龙湾",
    "city": "三亚",
    "province": "",
    "poi_type": "景点",
    "confidence": 0.8
  },
  {
    "poi_name": "亚龙湾的丽思卡尔顿酒店",
    "city": "三亚",
    "poi_type": "住宿",
    "confidence": 0.7
  },
  {
    "poi_name": "蜈支洲岛",
    "city": "三亚",
    "poi_type": "景点",
    "confidence": 0.7
  },
  {
    "poi_name": "海棠湾的免税店",
    "city": "三亚",
    "poi_type": "购物",
    "confidence": 0.6
  }
]
```

### 优缺点

**优点**：
- ✅ 免费，无需 API Key
- ✅ 支持非典型 POI（网红打卡点、小众地点）
- ✅ 可从社交媒体文本提取
- ✅ 支持评论中的 POI 挖掘

**缺点**：
- ❌ 依赖文本质量
- ❌ 无法获取精确经纬度
- ❌ 无法获取电话、营业时间等详情

---

## 方案五：Mapbox Places API

**文档**：https://www.mapbox.com/places-api

### 特点

| 特性 | 说明 |
|------|------|
| **开源友好** | 基于 OpenStreetMap |
| **自定义强** | 可定制地图样式 |
| **价格透明** | 免费额度充足 |

### 价格

- **免费**：50000 次/月（非常慷慨）

---

## 综合对比

### 传统 POI 提取（店铺/景点/地标）

| 需求 | 推荐方案 |
|------|---------|
| **国内** | 高德地图 API |
| **国际** | Google Places API |
| **免费** | 高德（5000 次/日） |
| **非典型 POI** | Foursquare + 文本提取 |

### 非典型 POI 提取（网红点/小众地点）

| 需求 | 推荐方案 |
|------|---------|
| **社交媒体** | POI 文本提取技能 |
| **实时热门** | Foursquare Trending |
| **用户评价** | Foursquare Tips |

---

## 推荐架构

### 最佳组合方案

```
┌─────────────────────────────────────┐
│         用户输入/社交媒体文本         │
└─────────────────┬───────────────────┘
                  │
         ┌────────▼────────┐
         │  POI 文本提取技能  │ ← 非典型 POI
         │  (已有，免费)    │
         └────────┬────────┘
                  │
         ┌────────▼────────┐
         │  高德/Google API │ ← 传统 POI 补全
         │  (获取经纬度等)  │
         └────────┬────────┘
                  │
         ┌────────▼────────┐
         │   去重 + 融合    │
         └────────┬────────┘
                  │
         ┌────────▼────────┐
         │    结构化输出    │
         └─────────────────┘
```

---

## 使用示例

### 示例 1：从文本提取 POI

```python
from poi_extractor import POIExtractor

extractor = POIExtractor()

text = """
刚从三亚回来，强烈推荐几个地方：
1. 亚龙湾的丽思卡尔顿酒店，海景超美
2. 蜈支洲岛潜水，海水清澈
3. 海棠湾免税店，购物天堂
4. 第一市场吃海鲜，便宜新鲜
"""

# 提取 POI
pois = extractor.extract_from_text(text)

for poi in pois:
    print(f"{poi.poi_name} ({poi.poi_type}) - {poi.city}")
```

### 示例 2：调用高德 API 补全

```python
import requests

AMAP_KEY = "你的 key"

def get_poi_details(poi_name, city):
    url = "https://restapi.amap.com/v3/place/text"
    params = {
        "keywords": poi_name,
        "city": city,
        "key": AMAP_KEY,
        "extensions": "all"
    }
    response = requests.get(url, params=params)
    data = response.json()
    
    if data["pois"]:
        poi = data["pois"][0]
        return {
            "name": poi["name"],
            "address": poi["address"],
            "location": poi["location"],  # 经纬度
            "tel": poi.get("tel", ""),
            "rating": poi.get("biz_ext", {}).get("rating", ""),
            "photos": [p["url"] for p in poi.get("photos", [])]
        }
```

---

## 成本估算

### 场景：每日处理 1000 条社交媒体帖子

| 方案 | 日调用量 | 月成本 |
|------|---------|--------|
| **高德 API** | 1000 次 | 免费（5000 次/日额度） |
| **Google Places** | 1000 次 | 免费（$200/月额度） |
| **Foursquare** | 1000 次 | 免费（$200/月额度） |
| **POI 文本提取** | 不限 | 免费 |

---

## 下一步

### 立即可用

1. **已有技能**：`poi-extractor` 可直接使用
2. **高德 API**：注册获取 Key（免费）
3. **Google Places**：注册获取 Key（$200 免费/月）

### 优化方向

1. **融合方案**：文本提取 + API 补全
2. **扩展地名库**：添加更多县市
3. **LLM 增强**：用大模型提升提取准确率
4. **实时热度**：结合社交媒体互动数据

---

## 相关资源

| 资源 | 链接 |
|------|------|
| 高德开放平台 | https://lbs.amap.com |
| Google Places | https://developers.google.com/maps/documentation/places |
| Foursquare | https://foursquare.com/developer |
| POI 分类编码表 | https://lbs.amap.com/api/webservice/download |

---

_需要我帮你配置高德 API 或优化 POI 提取技能吗？_
