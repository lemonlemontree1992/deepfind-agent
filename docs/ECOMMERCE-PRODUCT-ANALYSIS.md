# 🛍️ 电商产品方案分析Agent设计

## 📋 核心需求分析

### 当前问题
- ❌ 爬虫无法获取京东/淘宝商家后台数据（需要登录态）
- ❌ 公开页面数据不精确（价格、销量、评分可能不准确）
- ❌ 无法获取用户行为数据（转化率、停留时长、跳失率）
- ❌ 无法获取竞品数据（竞品销量、流量来源）

### 核心需求
- ✅ 输出**产品方案设计报告**（包含数据支撑）
- ✅ 获取**电商商家后台数据**（合法途径）
- ✅ 了解**电商平台数据字段结构**
- ✅ 进行**竞品对比分析**

---

## 🏗️ 电商商家后台数据字段结构

### 一、商品数据（Product Data）

#### 1.1 基础信息字段
```json
{
  "product_id": "12345678",              // 商品ID
  "spu_id": "987654321",                 // SPU ID（标准产品单元）
  "sku_id": "111222333",                 // SKU ID（库存单元）
  "title": "iPhone 15 Pro 256GB 幻影黑", // 商品标题
  "sub_title": "苹果官网正品...",         // 副标题
  "category_id": "1512",                 // 类目ID
  "category_path": "手机/手机通讯/手机",  // 类目路径
  "brand_id": "apple",                   // 品牌ID
  "brand_name": "Apple",                 // 品牌名称
  "product_url": "https://...",          // 商品详情页URL
  "main_image": "https://...",           // 主图URL
  "detail_images": ["https://..."],      // 详情图URL列表
  "video_url": "https://...",            // 视频URL
  "status": "onsale",                    // 商品状态（onsale/offsale/deleted）
  "created_at": "2024-09-15 10:00:00",   // 创建时间
  "updated_at": "2024-09-20 15:30:00"    // 更新时间
}
```

#### 1.2 价格库存字段
```json
{
  "price": 8999.00,                      // 当前售价（元）
  "original_price": 9999.00,             // 原价/划线价
  "cost_price": 7500.00,                 // 成本价（商家后台可见）
  "profit_margin": 16.67,                // 利润率（%）
  "stock": 1500,                          // 当前库存
  "stock_warning": 100,                   // 库存预警值
  "sold_count": 3250,                     // 累计销量
  "monthly_sold": 856,                    // 月销量
  "daily_sold": 28,                       // 日销量
  "sku_list": [                           // SKU列表（多规格商品）
    {
      "sku_id": "111222333",
      "spec": "幻影黑 256GB",
      "price": 8999.00,
      "stock": 500,
      "sold": 120
    },
    {
      "sku_id": "111222334",
      "spec": "银色 512GB",
      "price": 10899.00,
      "stock": 300,
      "sold": 85
    }
  ]
}
```

#### 1.3 评价数据字段
```json
{
  "rating_avg": 4.8,                      // 平均评分
  "rating_count": 12580,                  // 评价总数
  "rating_distribution": {                // 评分分布
    "5_star": 10500,                      // 5星评价数
    "4_star": 1500,                       // 4星评价数
    "3_star": 400,                        // 3星评价数
    "2_star": 120,                        // 2星评价数
    "1_star": 60                          // 1星评价数
  },
  "review_tags": [                        // 评价标签（关键词提取）
    {
      "tag": "物流快",
      "count": 8500,
      "sentiment": "positive"
    },
    {
      "tag": "包装好",
      "count": 7200,
      "sentiment": "positive"
    },
    {
      "tag": "发热严重",
      "count": 450,
      "sentiment": "negative"
    },
    {
      "tag": "续航一般",
      "count": 320,
      "sentiment": "negative"
    }
  ],
  "review_samples": [                     // 评价样例
    {
      "user": "用户XXX",
      "rating": 5,
      "content": "手机很好用，物流很快...",
      "created_at": "2024-09-18",
      "images": ["https://..."],
      "is_verified": true                  // 是否已确认购买
    }
  ],
  "qa_count": 1560,                       // 问答数量
  "qa_samples": [                         // 问答样例
    {
      "question": "支持双卡吗？",
      "answer": "支持双卡双待",
      "ask_count": 850
    }
  ]
}
```

---

### 二、流量数据（Traffic Data）

#### 2.1 访问数据字段
```json
{
  "pv": 125600,                           // 页面浏览量（PV）
  "uv": 45200,                            // 访客数（UV）
  "pv_uv_ratio": 2.78,                    // 人均浏览次数
  "avg_stay_time": 125,                   // 平均停留时长（秒）
  "bounce_rate": 35.2,                    // 跳失率（%）
  "new_visitor_ratio": 62.5,              // 新访客占比（%）
  "return_visitor_ratio": 37.5,           // 老访客占比（%）
  
  "traffic_sources": [                    // 流量来源分布
    {
      "source": "搜索",
      "pv": 50000,
      "uv": 18000,
      "ratio": 39.8
    },
    {
      "source": "推荐",
      "pv": 35000,
      "uv": 12500,
      "ratio": 27.9
    },
    {
      "source": "广告",
      "pv": 25000,
      "uv": 9000,
      "ratio": 19.9
    },
    {
      "source": "直接访问",
      "pv": 15600,
      "uv": 5700,
      "ratio": 12.4
    }
  ],
  
  "search_keywords": [                    // 搜索关键词
    {
      "keyword": "iPhone 15 Pro",
      "pv": 25000,
      "uv": 12000,
      "ctr": 5.2
    },
    {
      "keyword": "苹果15 Pro",
      "pv": 18000,
      "uv": 8500,
      "ctr": 4.8
    },
    {
      "keyword": "iPhone 15 Pro 幻影黑",
      "pv": 12000,
      "uv": 6000,
      "ctr": 6.5
    }
  ],
  
  "device_distribution": {                // 设备分布
    "mobile": {
      "pv": 87500,
      "uv": 31500,
      "ratio": 69.7
    },
    "pc": {
      "pv": 38100,
      "uv": 13700,
      "ratio": 30.3
    }
  },
  
  "geo_distribution": [                   // 地域分布
    {
      "province": "广东",
      "uv": 8500,
      "ratio": 18.8
    },
    {
      "province": "北京",
      "uv": 6200,
      "ratio": 13.7
    },
    {
      "province": "上海",
      "uv": 5800,
      "ratio": 12.8
    }
  ]
}
```

#### 2.2 转化数据字段
```json
{
  "impression": 1250000,                  // 曝光量
  "click": 45200,                         // 点击量
  "ctr": 3.62,                            // 点击率（%）
  "add_to_cart": 8500,                    // 加购数
  "add_to_cart_rate": 18.8,               // 加购率（%）
  "order_count": 1250,                    // 订单数
  "order_uv": 1150,                       // 下单人数
  "order_amount": 11250000,               // 订单金额（分）
  "conversion_rate": 2.76,                // 转化率（%）
  "avg_order_value": 9000,                // 客单价（元）
  "gmv": 11250000,                        // GMV（交易总额，分）
  
  "conversion_funnel": [                  // 转化漏斗
    {
      "step": "曝光",
      "count": 1250000,
      "ratio": 100.0
    },
    {
      "step": "点击",
      "count": 45200,
      "ratio": 3.62
    },
    {
      "step": "加购",
      "count": 8500,
      "ratio": 0.68
    },
    {
      "step": "下单",
      "count": 1250,
      "ratio": 0.10
    },
    {
      "step": "支付",
      "count": 1150,
      "ratio": 0.09
    }
  ],
  
  "cart_abandonment": {                   // 购物车放弃分析
    "add_to_cart": 8500,
    "order": 1250,
    "abandon_rate": 85.3
  }
}
```

---

### 三、订单数据（Order Data）

#### 3.1 订单基础字段
```json
{
  "order_id": "2024092012345678",          // 订单ID
  "order_status": "completed",             // 订单状态
  "payment_status": "paid",                // 支付状态
  "shipping_status": "delivered",          // 物流状态
  
  "buyer_id": "user_123456",               // 买家ID
  "buyer_type": "new",                     // 买家类型（new/return）
  "buyer_level": "gold",                   // 会员等级
  
  "product_list": [                        // 商品列表
    {
      "sku_id": "111222333",
      "product_name": "iPhone 15 Pro 256GB 幻影黑",
      "quantity": 1,
      "unit_price": 8999.00,
      "discount": 100.00,
      "final_price": 8899.00
    }
  ],
  
  "order_amount": {                        // 订单金额明细
    "product_amount": 8899.00,             // 商品金额
    "shipping_fee": 0,                     // 运费
    "discount_amount": 100.00,             // 优惠金额
    "final_amount": 8899.00                // 实付金额
  },
  
  "payment": {                             // 支付信息
    "payment_method": "alipay",            // 支付方式
    "payment_time": "2024-09-20 15:30:00",
    "transaction_id": "2024092012345678"
  },
  
  "shipping": {                            // 物流信息
    "shipping_method": "顺丰速运",
    "tracking_number": "SF1234567890",
    "shipped_at": "2024-09-20 18:00:00",
    "delivered_at": "2024-09-22 10:30:00",
    "delivery_time": 41.5                   // 配送时长（小时）
  },
  
  "created_at": "2024-09-20 15:25:00",     // 下单时间
  "updated_at": "2024-09-22 10:30:00"      // 更新时间
}
```

#### 3.2 订单统计字段
```json
{
  "total_orders": 1250,                    // 订单总数
  "completed_orders": 1150,                // 已完成订单
  "cancelled_orders": 100,                 // 取消订单
  
  "order_status_distribution": {           // 订单状态分布
    "pending_payment": 50,
    "paid": 30,
    "shipped": 20,
    "delivered": 1150,
    "cancelled": 100
  },
  
  "order_time_distribution": [             // 下单时间分布
    {
      "hour": "10:00-12:00",
      "order_count": 180,
      "ratio": 14.4
    },
    {
      "hour": "14:00-16:00",
      "order_count": 220,
      "ratio": 17.6
    },
    {
      "hour": "20:00-22:00",
      "order_count": 280,
      "ratio": 22.4
    }
  ],
  
  "repeat_purchase_rate": 28.5,            // 复购率（%）
  "avg_delivery_time": 42.3                // 平均配送时长（小时）
}
```

---

### 四、竞品数据（Competitor Data）

#### 4.1 竞品基础信息
```json
{
  "competitor_product": {
    "platform": "jd",                      // 平台（jd/tmall/taobao）
    "product_id": "987654321",
    "title": "华为 Mate 60 Pro 256GB 雅丹黑",
    "brand": "华为",
    "category": "手机",
    
    "price_monitoring": {                  // 价格监控（商家后台功能）
      "current_price": 6999.00,
      "price_history": [
        {"date": "2024-09-01", "price": 6999.00},
        {"date": "2024-09-10", "price": 6899.00},
        {"date": "2024-09-15", "price": 6999.00}
      ],
      "lowest_price": 6899.00,
      "highest_price": 7199.00,
      "avg_price": 7032.00,
      "price_change_frequency": 3           // 价格变动次数
    },
    
    "sales_monitoring": {                  // 销量监控（商家后台功能）
      "daily_sold": 32,
      "monthly_sold": 960,
      "total_sold": 4580,
      "sales_trend": [
        {"date": "2024-09-01", "sold": 25},
        {"date": "2024-09-02", "sold": 28},
        {"date": "2024-09-03", "sold": 35}
      ]
    },
    
    "ranking_monitoring": {                // 排名监控
      "category_rank": 5,                  // 类目排名
      "brand_rank": 2,                     // 品牌排名
      "search_rank": {                     // 搜索排名
        "iPhone 15 Pro": 1,
        "华为 Mate 60 Pro": 5,
        "小米 14 Pro": 8
      }
    },
    
    "traffic_monitoring": {                // 流量监控（估算）
      "estimated_pv": 150000,
      "estimated_uv": 54000,
      "traffic_source": {
        "search": 45.2,
        "recommend": 30.5,
        "ad": 24.3
      }
    }
  }
}
```

#### 4.2 竞品对比分析
```json
{
  "comparison": {
    "my_product": {
      "product_name": "iPhone 15 Pro",
      "price": 8999.00,
      "monthly_sold": 856,
      "rating_avg": 4.8,
      "rating_count": 12580,
      "conversion_rate": 2.76,
      "ctr": 3.62,
      "category_rank": 1
    },
    
    "competitor_products": [
      {
        "product_name": "华为 Mate 60 Pro",
        "price": 6999.00,
        "monthly_sold": 960,
        "rating_avg": 4.7,
        "rating_count": 15200,
        "conversion_rate": 2.85,
        "ctr": 3.95,
        "category_rank": 2,
        "price_gap": -2000.00,                // 价格差距
        "sales_gap": 104,                     // 销量差距
        "advantage": ["性价比高", "国产芯片"],
        "disadvantage": ["影像略弱", "生态不完善"]
      },
      {
        "product_name": "小米 14 Pro",
        "price": 4999.00,
        "monthly_sold": 1250,
        "rating_avg": 4.6,
        "rating_count": 9800,
        "conversion_rate": 3.12,
        "ctr": 4.25,
        "category_rank": 3,
        "price_gap": -4000.00,
        "sales_gap": 394,
        "advantage": ["价格优势", "性价比"],
        "disadvantage": ["品牌力弱", "影像一般"]
      }
    ],
    
    "market_position": {                    // 市场定位分析
      "my_product": {
        "position": "高端旗舰",
        "target_user": "追求品质、预算充足",
        "market_share": 25.3
      },
      "competitor_1": {
        "position": "高端旗舰",
        "target_user": "支持国货、追求性价比",
        "market_share": 28.5
      },
      "competitor_2": {
        "position": "性价比旗舰",
        "target_user": "追求性价比、预算有限",
        "market_share": 15.2
      }
    }
  }
}
```

---

### 五、营销数据（Marketing Data）

#### 5.1 促销活动数据
```json
{
  "campaign_id": "double11_2024",          // 活动ID
  "campaign_name": "双11大促",
  "campaign_type": "festival",             // 活动类型
  "start_time": "2024-11-01 00:00:00",
  "end_time": "2024-11-11 23:59:59",
  
  "discount_rules": {                      // 优惠规则
    "full_reduction": "满5000减500",
    "coupon": ["满3000减200", "满5000减400"],
    "gift": ["赠送手机壳", "赠送贴膜"],
    "interest_free": "12期免息"
  },
  
  "performance": {                         // 活动表现
    "exposure": 2500000,                   // 曝光量
    "click": 125000,                       // 点击量
    "ctr": 5.0,                            // 点击率
    "order_count": 3500,                   // 订单数
    "order_amount": 31500000,              // 订单金额（分）
    "conversion_rate": 2.8,                // 转化率
    "roi": 4.5                             // ROI（投入产出比）
  },
  
  "traffic_source": {                      // 流量来源
    "search": {
      "uv": 45000,
      "order": 1200,
      "conversion_rate": 2.67
    },
    "recommend": {
      "uv": 35000,
      "order": 1100,
      "conversion_rate": 3.14
    },
    "ad": {
      "uv": 25000,
      "order": 800,
      "conversion_rate": 3.2
    },
    "live_stream": {                       // 直播带货
      "uv": 20000,
      "order": 400,
      "conversion_rate": 2.0
    }
  }
}
```

#### 5.2 广告投放数据
```json
{
  "ad_campaigns": [                        // 广告计划
    {
      "campaign_id": "ad_001",
      "campaign_name": "双十一搜索推广",
      "platform": "京东快车",
      "budget": 50000,                      // 预算（元）
      "cost": 42500,                        // 实际花费
      "budget_usage": 85.0,                 // 预算使用率
      
      "performance": {
        "impression": 2500000,              // 展示量
        "click": 125000,                    // 点击量
        "ctr": 5.0,                         // 点击率
        "cpc": 0.34,                        // 平均点击成本
        "order_count": 1500,                // 订单数
        "order_amount": 13500000,           // 订单金额（分）
        "cpa": 28.33,                       // 平均获客成本
        "roas": 3.18,                       // 广告支出回报率
        "conversion_rate": 1.2              // 转化率
      },
      
      "keywords": [                         // 关键词表现
        {
          "keyword": "iPhone 15 Pro",
          "impression": 850000,
          "click": 45000,
          "ctr": 5.29,
          "cpc": 0.35,
          "cost": 15750,
          "order": 650,
          "conversion_rate": 1.44,
          "roas": 3.85
        },
        {
          "keyword": "苹果手机",
          "impression": 600000,
          "click": 30000,
          "ctr": 5.0,
          "cpc": 0.32,
          "cost": 9600,
          "order": 350,
          "conversion_rate": 1.17,
          "roas": 2.84
        }
      ]
    }
  ]
}
```

---

## 🔍 合法获取商家后台数据的方案

### 方案一：电商开放平台API（推荐）

#### 1.1 淘宝开放平台
**官网**: https://open.taobao.com/
**适用场景**: 淘宝、天猫商家
**免费额度**: 部分API免费，超出收费
**申请条件**: 需要企业资质 + 淘宝店铺

**核心API**:
```python
# 淘宝开放平台API示例

# 1. 获取商品列表
api_url = "https://eco.taobao.com/router/rest"
params = {
    "method": "taobao.items.onsale.get",      # 获取在售商品
    "session": "ACCESS_TOKEN",                # 授权token
    "fields": "num_iid,title,price,quantity,sold_num",
    "page_no": 1,
    "page_size": 100
}

# 2. 获取商品详情
params = {
    "method": "taobao.item.seller.get",       # 获取商品详情
    "session": "ACCESS_TOKEN",
    "fields": "num_iid,title,price,quantity,sold_num,delist_time",
    "num_iid": "12345678"                     # 商品ID
}

# 3. 获取订单列表
params = {
    "method": "taobao.trades.sold.get",       # 获取订单列表
    "session": "ACCESS_TOKEN",
    "fields": "tid,status,created,modified,buyer_nick,payment",
    "start_created": "2024-09-01 00:00:00",
    "end_created": "2024-09-30 23:59:59"
}

# 4. 获取流量数据（生意参谋）
params = {
    "method": "taobao.sycm.trade.summary.get",  # 交易概览
    "session": "ACCESS_TOKEN",
    "date": "2024-09-20"
}
```

**申请流程**:
1. 注册淘宝开放平台账号
2. 创建应用（选择"商家应用"）
3. 提交企业资质审核（营业执照）
4. 申请API权限
5. 获取AppKey和AppSecret
6. 授权店铺（OAuth2.0）

---

#### 1.2 京东开放平台
**官网**: https://open.jd.com/
**适用场景**: 京东商家
**免费额度**: 部分API免费
**申请条件**: 需要京东店铺

**核心API**:
```python
# 京东开放平台API示例

# 1. 获取商品列表
api_url = "https://api.jd.com/routerjson"
params = {
    "method": "jingdong.ware.read.findWareById",
    "access_token": "ACCESS_TOKEN",
    "ware_id": "12345678"
}

# 2. 获取订单列表
params = {
    "method": "jingdong.order.search",
    "access_token": "ACCESS_TOKEN",
    "start_date": "2024-09-01 00:00:00",
    "end_date": "2024-09-30 23:59:59"
}

# 3. 获取流量数据（京东商智）
params = {
    "method": "jingdong.data.visitor.getPageView",
    "access_token": "ACCESS_TOKEN",
    "date": "2024-09-20"
}
```

---

#### 1.3 拼多多开放平台
**官网**: https://open.pinduoduo.com/
**适用场景**: 拼多多商家
**免费额度**: 部分API免费
**申请条件**: 需要拼多多店铺

**核心API**:
```python
# 拼多多开放平台API示例

# 1. 获取商品列表
api_url = "https://gw-api.pinduoduo.com/api/router"
params = {
    "type": "pdd.goods.sold.get",
    "access_token": "ACCESS_TOKEN"
}

# 2. 获取订单列表
params = {
    "type": "pdd.order.list.get",
    "access_token": "ACCESS_TOKEN",
    "start_confirm_at": "2024-09-01 00:00:00",
    "end_confirm_at": "2024-09-30 23:59:59"
}
```

---

### 方案二：商家后台数据导出（最简单）

所有电商平台都提供数据导出功能：

#### 2.1 淘宝/天猫 - 千牛工作台
**路径**: 千牛工作台 → 数据中心 → 生意参谋 → 下载数据

**可导出数据**:
- ✅ 商品数据（商品列表、价格、销量、库存）
- ✅ 订单数据（订单明细、退款订单）
- ✅ 流量数据（访客数、浏览量、跳失率）
- ✅ 交易数据（GMV、客单价、转化率）
- ✅ 竞品数据（竞品价格、销量监控）
- ✅ 营销数据（直通车、钻展、超级推荐）

**导出格式**: CSV/Excel

---

#### 2.2 京东 - 京东商智
**路径**: 京东商家后台 → 数据 → 商智 → 数据下载

**可导出数据**:
- ✅ 商品数据（SKU明细、价格、销量、库存）
- ✅ 订单数据（订单明细、售后订单）
- ✅ 流量数据（PV、UV、停留时长、跳失率）
- ✅ 交易数据（GMV、客单价、转化率）
- ✅ 竞品数据（竞品监控、价格监控）
- ✅ 广告数据（京东快车、京东展位）

**导出格式**: CSV/Excel

---

#### 2.3 拼多多 - 多多参谋
**路径**: 拼多多商家后台 → 数据中心 → 多多参谋 → 导出数据

**可导出数据**:
- ✅ 商品数据（商品列表、价格、销量）
- ✅ 订单数据（订单明细、售后订单）
- ✅ 流量数据（访客数、浏览量）
- ✅ 交易数据（GMV、客单价）
- ✅ 推广数据（多多搜索、多多场景）

**导出格式**: CSV/Excel

---

### 方案三：第三方数据分析工具

#### 3.1 生意参谋（淘宝/天猫官方）
**官网**: https://sycm.taobao.com/
**功能**:
- ✅ 行业洞察（行业大盘、品牌分析）
- ✅ 竞品监控（竞品价格、销量、流量）
- ✅ 流量分析（流量来源、访客分析）
- ✅ 交易分析（转化漏斗、客单价）
- ✅ 商品分析（爆款分析、滞销品）

**价格**: 
- 标准版：¥1800/年
- 专业版：¥3600/年
- 旗舰版：¥10800/年

---

#### 3.2 京东商智（京东官方）
**官网**: https://sz.jd.com/
**功能**:
- ✅ 行业分析（行业大盘、类目分析）
- ✅ 竞品分析（竞品监控、价格监测）
- ✅ 流量分析（流量来源、访客分析）
- ✅ 交易分析（成交分析、转化分析）
- ✅ 商品分析（商品排行、库存分析）

**价格**: 
- 基础版：免费
- 高级版：¥12000/年

---

#### 3.3 DataEye（第三方）
**官网**: https://www.dataeye.com/
**功能**:
- ✅ 全平台数据监控（淘宝、京东、拼多多、抖音）
- ✅ 竞品分析（价格监控、销量预测）
- ✅ 行业报告（行业趋势、品类分析）
- ✅ 舆情监控（用户评价、社交媒体）

**价格**: 
- 基础版：¥299/月
- 专业版：¥999/月
- 企业版：¥2999/月

---

#### 3.4 电商大数网（免费）
**官网**: http://www.dsda.cn/
**功能**:
- ✅ 行业数据（行业大盘、品类排行）
- ✅ 热销商品榜（销量排行、价格区间）
- ✅ 店铺排行（销量排行、评分排行）
- ✅ 关键词分析（热搜词、飙升词）

**价格**: 免费版可用，高级版¥199/月

---

### 方案四：电商数据API聚合服务

#### 4.1 企查查电商数据API
**官网**: https://openapi.qcc.com/
**功能**:
- ✅ 店铺信息查询
- ✅ 商品信息查询
- ✅ 销量数据估算
- ✅ 企业资质查询

**价格**: ¥1000-5000/月

---

#### 4.2 聚水潭电商ERP
**官网**: https://www.jushuitan.com/
**功能**:
- ✅ 多平台数据聚合（淘宝、京东、拼多多、抖音）
- ✅ 库存管理
- ✅ 订单管理
- ✅ 数据报表

**价格**: ¥1000-3000/月

---

## 🎯 产品方案分析Agent设计

### 一、输入设计

```python
class ProductAnalysisRequest(BaseModel):
    """产品分析请求"""
    
    # 基础信息
    product_name: str                      # 产品名称（如"iPhone 15 Pro"）
    category: str                          # 品类（如"手机"）
    brand: str                             # 品牌（如"Apple"）
    
    # 竞品信息
    competitor_products: List[str]         # 竞品列表（如["华为Mate 60 Pro", "小米14 Pro"]）
    
    # 数据源（可选）
    data_sources: List[str] = [            # 数据源
        "taobao_api",                      # 淘宝API
        "jd_api",                          # 京东API
        "pdd_api",                         # 拼多多API
        "sycm_export",                     # 生意参谋导出
        "third_party"                      # 第三方数据
    ]
    
    # 分析维度（可选）
    analysis_dimensions: List[str] = [     # 分析维度
        "price_strategy",                  # 价格策略
        "sales_trend",                     # 销量趋势
        "user_evaluation",                 # 用户评价
        "traffic_source",                  # 流量来源
        "conversion_funnel",               # 转化漏斗
        "competitor_comparison",           # 竞品对比
        "market_position"                  # 市场定位
    ]
    
    # 商家后台数据（用户上传）
    merchant_data: Optional[Dict] = {      # 商家后台数据（CSV导出）
        "products": None,                  # 商品数据CSV
        "orders": None,                    # 订单数据CSV
        "traffic": None,                   # 流量数据CSV
        "competitors": None                # 竞品数据CSV
    }
```

---

### 二、分析流程设计

```python
async def analyze_product_strategy(request: ProductAnalysisRequest):
    """产品方案分析主流程"""
    
    # Step 1: 数据采集（从多个数据源）
    data = await collect_data(request)
    
    # Step 2: 数据清洗和标准化
    cleaned_data = await clean_and_normalize(data)
    
    # Step 3: 多维度分析
    analysis_results = {}
    
    # 3.1 价格策略分析
    analysis_results["price_strategy"] = await analyze_price_strategy(
        cleaned_data["products"],
        cleaned_data["competitors"]
    )
    
    # 3.2 销量趋势分析
    analysis_results["sales_trend"] = await analyze_sales_trend(
        cleaned_data["products"],
        cleaned_data["orders"]
    )
    
    # 3.3 用户评价分析
    analysis_results["user_evaluation"] = await analyze_user_evaluation(
        cleaned_data["products"]
    )
    
    # 3.4 流量来源分析
    analysis_results["traffic_source"] = await analyze_traffic_source(
        cleaned_data["traffic"]
    )
    
    # 3.5 转化漏斗分析
    analysis_results["conversion_funnel"] = await analyze_conversion_funnel(
        cleaned_data["traffic"],
        cleaned_data["orders"]
    )
    
    # 3.6 竞品对比分析
    analysis_results["competitor_comparison"] = await analyze_competitor_comparison(
        cleaned_data["products"],
        cleaned_data["competitors"]
    )
    
    # 3.7 市场定位分析
    analysis_results["market_position"] = await analyze_market_position(
        cleaned_data["products"],
        cleaned_data["competitors"]
    )
    
    # Step 4: 生成产品方案报告
    report = await generate_product_strategy_report(
        request,
        analysis_results
    )
    
    return report
```

---

### 三、输出报告结构

```markdown
# [产品名] 产品方案分析报告

## 一、产品概览

### 1.1 基础信息
| 项目 | 数据 | 备注 |
|------|------|------|
| 产品名称 | iPhone 15 Pro | - |
| 品类 | 手机 | - |
| 品牌 | Apple | - |
| 当前售价 | ¥8999 | 官方价 |
| 月销量 | 856台 | 最近30天 |
| 累计销量 | 3,250台 | 上架以来 |
| 平均评分 | ⭐4.8/5 | 基于评分数据 |
| 评价数 | 12,580条 | - |

### 1.2 销售表现
| 指标 | 数据 | 行业平均 | 对比 |
|------|------|---------|------|
| 月GMV | ¥770.4万 | ¥520万 | +48% ✅ |
| 客单价 | ¥8,999 | ¥5,500 | +63% ✅ |
| 转化率 | 2.76% | 2.5% | +10% ✅ |
| 复购率 | 5.2% | 3.8% | +37% ✅ |

---

## 二、价格策略分析

### 2.1 价格历史走势
📈 **价格曲线图**（最近3个月）

| 时间 | 价格 | 促销 | 备注 |
|------|------|------|------|
| 2024-09-15 | ¥9,999 | 首发 | 官方首发价 |
| 2024-10-01 | ¥9,499 | 国庆优惠 | 降价¥500 |
| 2024-11-01 | ¥8,999 | 双11预售 | 降价¥500 |
| 2024-11-11 | ¥8,499 | 双11大促 | 历史最低价 |
| 2024-12-01 | ¥8,999 | 恢复原价 | 双11后回调 |

💡 **价格策略建议**:
- 当前价格接近历史最低点，性价比凸显
- 建议维持¥8,999价位，等待双12再降价至¥8,499
- 可叠加12期免息、赠送配件等促销手段

### 2.2 竞品价格对比
| 产品 | 当前价格 | 价格差距 | 促销力度 |
|------|---------|---------|---------|
| iPhone 15 Pro | ¥8,999 | 基准 | 双11降价¥500 |
| 华为Mate 60 Pro | ¥6,999 | -¥2,000 | 降价¥300 |
| 小米14 Pro | ¥4,999 | -¥4,000 | 降价¥200 |

💡 **定价建议**:
- 面对华为 Mate 60 Pro 的价格优势，建议主推"品牌力+影像能力"
- 面对小米 14 Pro 的性价比优势，建议强调"体验+生态"
- 不建议降价至¥8,000以下，避免品牌形象受损

---

## 三、销量趋势分析

### 3.1 销量趋势图
📈 **最近30天销量曲线图**

| 时间段 | 日均销量 | 环比变化 | 备注 |
|--------|---------|---------|------|
| 9月1-7日 | 18台/天 | - | 首发 week |
| 9月8-14日 | 22台/天 | +22% | 评价积累 |
| 9月15-21日 | 25台/天 | +14% | 国庆预热 |
| 9月22-30日 | 32台/天 | +28% | 国庆假期 |
| 10月1-7日 | 28台/天 | -12% | 假期结束 |
| 10月8-15日 | 26台/天 | -7% | 正常波动 |

💡 **销量趋势分析**:
- 首发后销量稳步上升，评价积累是关键
- 国庆假期是销量高峰，日销32台
- 双11期间预计日均销量可达50台以上

### 3.2 类目排名
| 排名维度 | 当前排名 | 上月排名 | 变化 |
|---------|---------|---------|------|
| 类目排名 | 第1名 | 第1名 | 持平 |
| 品牌排名 | 第1名 | 第1名 | 持平 |
| 搜索排名("手机") | 第3名 | 第5名 | ↑2名 |

---

## 四、用户评价分析

### 4.1 评价分布
| 评分 | 数量 | 占比 | 典型评价 |
|------|------|------|---------|
| ⭐⭐⭐⭐⭐ | 10,500 | 83.5% | "非常好用，物流超快" |
| ⭐⭐⭐⭐ | 1,500 | 11.9% | "整体不错，续航一般" |
| ⭐⭐⭐ | 400 | 3.2% | "发热明显，价格偏高" |
| ⭐⭐ | 120 | 1.0% | "续航太差，不推荐" |
| ⭐ | 60 | 0.5% | "质量有问题，售后差" |

### 4.2 评价关键词云
**正向评价 TOP5**:
1. **物流快** (8,500次提及, 67.6%)
2. **包装好** (7,200次提及, 57.2%)
3. **手感好** (6,800次提及, 54.1%)
4. **影像强** (6,500次提及, 51.7%)
5. **系统流畅** (6,200次提及, 49.3%)

**负向评价 TOP5**:
1. **发热严重** (450次提及, 3.6%)
2. **续航一般** (320次提及, 2.5%)
3. **价格偏高** (280次提及, 2.2%)
4. **信号一般** (150次提及, 1.2%)
5. **充电慢** (120次提及, 1.0%)

### 4.3 用户画像
| 用户类型 | 占比 | 典型需求 | 购买决策因素 |
|---------|------|---------|------------|
| 追求品质 | 45% | 品牌力、体验、生态 | 品牌口碑、用户评价 |
| 商务人士 | 30% | 续航、信号、效率 | 续航、信号、办公功能 |
| 预算敏感 | 25% | 价格、性价比 | 价格、促销力度 |

💡 **产品优化建议**:
- **发热问题**: 建议在详情页增加散热设计说明，降低用户预期
- **续航问题**: 建议推荐MagSafe外接电池，提升续航体验
- **价格问题**: 建议提供12期免息、以旧换新等方案，降低购买门槛

---

## 五、流量来源分析

### 5.1 流量来源分布
| 来源 | UV | 占比 | CTR | 转化率 | 贡献度 |
|------|-----|------|-----|--------|--------|
| 搜索流量 | 18,000 | 39.8% | 5.2% | 2.8% | ⭐⭐⭐⭐⭐ |
| 推荐流量 | 12,500 | 27.9% | 4.5% | 2.5% | ⭐⭐⭐⭐ |
| 广告流量 | 9,000 | 19.9% | 3.8% | 3.2% | ⭐⭐⭐⭐⭐ |
| 直接访问 | 5,700 | 12.4% | - | 2.9% | ⭐⭐⭐ |

💡 **流量优化建议**:
- **搜索流量**: 优化标题关键词（增加"降价"、"双11"等热搜词）
- **推荐流量**: 提升商品评分至4.9分，增加推荐权重
- **广告流量**: 增加双11广告预算，ROI高达3.18，可持续投入

### 5.2 搜索关键词分析
| 关键词 | UV | CTR | 转化率 | 备注 |
|--------|-----|------|--------|------|
| iPhone 15 Pro | 12,000 | 5.8% | 2.9% | 核心词，自然流量 |
| 苹果15 Pro | 8,500 | 5.2% | 2.7% | 核心词，自然流量 |
| iPhone 15 Pro 幻影黑 | 6,000 | 6.5% | 3.1% | 精准词，转化高 |
| iPhone 15 Pro 降价 | 3,500 | 7.2% | 4.5% | 热搜词，转化极高 |
| iPhone 15 Pro 双11 | 2,800 | 8.0% | 5.2% | 热搜词，转化极高 |

💡 **关键词优化建议**:
- 增加热搜词："降价"、"双11"、"优惠"、"免息"
- 增加精准词："幻影黑"、"256GB"、"512GB"
- 增加关联词："iPhone 15 Pro vs 华为Mate 60 Pro"

---

## 六、转化漏斗分析

### 6.1 转化漏斗
```
曝光 1,250,000 (100%)
   ↓ 点击率 3.62%
点击 45,200 (3.62%)
   ↓ 加购率 18.8%
加购 8,500 (0.68%)
   ↓ 转化率 14.7%
下单 1,250 (0.10%)
   ↓ 支付率 92%
支付 1,150 (0.09%)
```

### 6.2 各环节优化建议

**曝光 → 点击 (CTR 3.62%)**:
- 💡 优化主图：增加促销标签（双11降价¥500）
- 💡 优化标题：增加热搜词（降价、双11、免息）
- 💡 优化价格：显示划线价¥9,999，突出优惠

**点击 → 加购 (加购率 18.8%)**:
- 💡 优化详情页：展示用户好评、视频评测
- 💡 增加促销：限时优惠、赠品（手机壳、贴膜）
- 💡 提升信任：增加"正品保证"、"假一赔十"

**加购 → 下单 (转化率 14.7%)**:
- 💡 优惠提醒：购物车页面显示"降价提醒"
- 💡 库存警告：显示"仅剩XX件"，制造紧迫感
- 💡 支付便捷：支持花呗、京东白条、12期免息

**下单 → 支付 (支付率 92%)**:
- 💡 未支付提醒：下单后30分钟未支付，发送短信提醒
- 💡 支付优化：简化支付流程，减少步骤
- 💡 优惠倒计时：显示"优惠剩余XX分钟"

---

## 七、竞品对比分析

### 7.1 竞品基础对比表
| 项目 | iPhone 15 Pro | 华为Mate 60 Pro | 小米14 Pro |
|------|--------------|-----------------|-----------|
| **价格** | ¥8,999 | ¥6,999 | ¥4,999 |
| **月销量** | 856台 | 960台 | 1,250台 |
| **评分** | ⭐4.8 | ⭐4.7 | ⭐4.6 |
| **评价数** | 12,580 | 15,200 | 9,800 |
| **转化率** | 2.76% | 2.85% | 3.12% |
| **CTR** | 3.62% | 3.95% | 4.25% |
| **类目排名** | 第1名 | 第2名 | 第3名 |

### 7.2 竞品优势劣势对比
**iPhone 15 Pro**:
- ✅ 优势：品牌力强、影像优秀、生态完善
- ❌ 劣势：价格偏高、续航一般、发热明显

**华为Mate 60 Pro**:
- ✅ 优势：性价比高、国产芯片、影像优秀
- ❌ 劣势：发热明显、生态不完善、信号一般

**小米14 Pro**:
- ✅ 优势：价格优势、性价比高、配置均衡
- ❌ 劣势：品牌力弱、影像一般、品控不稳定

### 7.3 竞品定价策略对比
| 品牌 | 定价策略 | 价格区间 | 促销力度 |
|------|---------|---------|---------|
| Apple | 高价策略 | ¥8,999-13,999 | 降价¥500-1000 |
| 华为 | 差异化定价 | ¥6,999-9,999 | 降价¥300-500 |
| 小米 | 性价比定价 | ¥4,999-6,999 | 降价¥200-300 |

---

## 八、市场定位分析

### 8.1 市场定位图
```
价格
高 │
   │        ● iPhone 15 Pro
   │       (高端旗舰)
   │
中 │               ● 华为Mate 60 Pro
   │              (高端性价比)
   │
低 │                       ● 小米14 Pro
   │                      (性价比旗舰)
   └───────────────────────────────── 性能
```

### 8.2 目标用户画像
iPhone 15 Pro 目标用户:
- **年龄段**: 25-40岁
- **收入水平**: 月薪1.5万+
- **职业**: 企业高管、白领、自由职业者
- **消费心理**: 追求品质、重视品牌、愿意为体验付费
- **购买决策因素**: 品牌口碑(35%)、用户评价(28%)、价格(22%)、配置(15%)

---

## 九、产品方案建议

### 9.1 定价策略
**建议定价**: ¥8,999（维持当前价位）

**促销策略**:
1. **双11大促**: 降价至¥8,499（历史最低价）
2. **叠加优惠**: 12期免息 + 赠送AirPods Pro（价值¥1,999）
3. **以旧换新**: iPhone 14 Pro Max 最高抵扣¥3,000
4. **会员专享**: 京东Plus会员额外优惠¥200

**价格保护**:
- 承诺"买贵赔差"，消除用户价格顾虑
- 提供"30天价保"，双11后降价可退差价

### 9.2 流量策略
**搜索优化**:
- 增加热搜词："双11降价"、"12期免息"、"以旧换新"
- 优化标题：iPhone 15 Pro 256GB 幻影黑 双11降价¥500 12期免息

**广告投放**:
- 双11期间增加广告预算至¥100,000（ROI预期4.0+）
- 重点投放关键词："iPhone 15 Pro 降价"、"iPhone 15 Pro 双11"
- 投放时段：晚上20:00-22:00（转化率最高）

**内容营销**:
- 制作开箱视频、评测视频，投放B站、抖音
- 邀请KOL评测，重点强调"影像升级"、"性能强劲"
- 发布用户真实评价合集，提升信任度

### 9.3 转化优化
**详情页优化**:
- 增加"用户评价"模块，展示真实好评
- 增加"竞品对比"模块，突出iPhone 15 Pro优势
- 增加"常见问题"模块，解答续航、发热等问题

**促销工具**:
- 设置"限时优惠"，营造紧迫感
- 设置"库存预警"，显示"仅剩50件"
- 提供"12期免息"，降低购买门槛

### 9.4 用户运营
**老用户召回**:
- 发送短信："您的iPhone 12已使用3年，iPhone 15 Pro性能提升50%，以旧换新最高抵扣¥3,000"

**会员运营**:
- 京东Plus会员专享优惠¥200
- 提供AppleCare+延保服务，提升用户信心

**售后服务**:
- 提供"7天无理由退货"，降低购买风险
- 提供"假一赔十"，提升正品信任度
- 提供"30天价保"，消除价格顾虑

---

## 十、风险提示

### 10.1 竞品风险
- **华为Mate 60 Pro**: 国产芯片情怀加持，销量持续增长，建议强化品牌力
- **小米14 Pro**: 价格优势明显，建议强调体验和生态优势

### 10.2 价格风险
- 当前价格接近历史最低点，双11后可能回调至¥8,999
- 建议提供30天价保，消除用户价格顾虑

### 10.3 库存风险
- 当前库存1,500台，双11期间预计销量3,000台
- 建议提前备货至5,000台，避免缺货

### 10.4 评价风险
- 负向评价主要集中在"发热"、"续航"
- 建议在详情页增加散热设计说明，降低用户预期

---

## 十一、行动清单

### 短期（1周内）
- [ ] 优化标题：增加"双11降价"、"12期免息"
- [ ] 优化主图：增加促销标签
- [ ] 设置双11预售：降价至¥8,499
- [ ] 增加广告预算：¥100,000

### 中期（1个月内）
- [ ] 制作开箱视频、评测视频
- [ ] 邀请KOL评测
- [ ] 发布用户真实评价合集
- [ ] 优化详情页：增加竞品对比模块

### 长期（3个月内）
- [ ] 建立用户社群，收集反馈
- [ ] 定期分析竞品动态，调整策略
- [ ] 建立品牌口碑，提升复购率

---

**报告生成时间**: 2024-09-20
**数据来源**: 淘宝开放平台API、京东开放平台API、生意参谋导出数据
**数据有效期**: 本报告数据截至2024-09-20，建议每月更新一次
```

---

## 🚀 实施路线图

### 第一阶段：数据源对接（2周）

**Week 1: API接入**
- Day 1-2: 淘宝开放平台申请（企业资质审核）
- Day 3-4: 京东开放平台申请
- Day 5-7: API对接开发

**Week 2: 数据导出功能集成**
- Day 1-3: 集成生意参谋数据导出
- Day 4-5: 集成京东商智数据导出
- Day 6-7: 数据清洗和标准化

---

### 第二阶段：分析模块开发（3周）

**Week 3: 基础分析模块**
- 价格策略分析
- 销量趋势分析
- 用户评价分析

**Week 4: 高级分析模块**
- 流量来源分析
- 转化漏斗分析
- 竞品对比分析

**Week 5: 报告生成模块**
- Markdown报告生成
- 数据可视化（图表）
- PDF导出功能

---

### 第三阶段：测试与优化（1周）

**Week 6: 测试与优化**
- 数据准确性测试
- 报告质量测试
- 性能优化
- 用户反馈收集

---

## 💰 成本预估

| 方案 | 月成本 | 开发周期 | 数据质量 | 推荐度 |
|------|--------|---------|---------|--------|
| **API方案** | ¥1000-5000 | 2-3周 | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ |
| **数据导出方案** | ¥0 | 1-2周 | ⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ |
| **第三方工具方案** | ¥500-3000 | 1周 | ⭐⭐⭐⭐ | ⭐⭐⭐⭐ |
| **混合方案** | ¥1000-2000 | 2-3周 | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ |

---

## 📝 总结

### 核心要点
1. **数据源选择**：电商开放平台API是最可靠的数据源
2. **报告结构**：基于电商商家后台数据字段设计，输出可执行的产品方案
3. **实施建议**：先使用数据导出方案验证效果，再考虑API对接

### 下一步行动
1. 确认数据源方案（API or 数据导出）
2. 申请电商开放平台权限
3. 开发数据采集和分析模块
4. 生成第一份产品方案分析报告

---

**文档版本**: V1.0
**创建时间**: 2024-09-20
**最后更新**: 2024-09-20