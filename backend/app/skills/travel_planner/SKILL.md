# Travel Planner Skill

## Version
1.0.0

## Description
旅游规划技能根据用户指定的城市、天数和季节，为用户生成科学合理的旅游行程安排。该技能会综合考虑天气情况、景点特色、交通便利性等因素，给出每日的详细活动安排、就餐建议和注意事项。

## Use Cases
- 生成3-7天的城市旅游计划
- 根据天气预报调整行程（如：雨天改为室内活动）
- 提供景点游览顺序和交通建议
- 推荐当地特色美食和购物地点
- 生成包含时间安排的详细行程表

## Usage Guide

### Step 1: Understand User Requirements
从用户输入中提取：
- 目标城市
- 旅游天数
- 出行时间（季节/月份）
- 特殊需求（如有老人小孩同行、轮椅需求等）

### Step 2: Gather Information
结合以下信息制定计划：
- 天气数据（来自 weather_query 技能）
- 城市热门景点
- 交通信息
- 当地特色

### Step 3: Generate Daily Plan
为每一天生成：
- 上午活动（9:00-12:00）
- 午餐推荐
- 下午活动（14:00-18:00）
- 晚餐推荐
- 晚上活动（可选）

### Step 4: Add Tips
添加实用贴士：
- 穿着建议
- 必备物品清单
- 注意事项

## Parameters
- `city` (string, Required): 目标城市名称
- `days` (integer, Required): 旅游天数（1-7天）
- `weather_data` (object, Optional): 天气预报数据，如有则据此优化行程
- `preferences` (object, Optional): 用户偏好设置

## Precautions
- 行程不要安排太紧凑，留出休息时间
- 户外活动需关注天气预报，恶劣天气提前调整
- 考虑交通时间，不要跨区移动太频繁
- 餐厅推荐要考虑午晚餐时间
- 旅游旺季需提前预订门票/酒店
- 老年人行程强度要降低

## Reference Materials
- `popular_spots.json`: 城市热门景点数据
- `travel_tips.md`: 出行必备知识

## Execution Script
执行脚本位于 `./script.py`
