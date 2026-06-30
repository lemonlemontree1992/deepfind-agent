# 🚀 快速开始 - 本地调试

## 1. 环境准备（5分钟）

### 1.1 复制环境变量
```bash
cd /Users/purepure/Desktop/docs/deepfind-agent/test
cp local_config/.env.local.example local_config/.env.local
```

### 1.2 编辑环境变量
```bash
vim local_config/.env.local
```

填入实际的API Key：
- `DEEPSEEK_API_KEY`: 已有
- `TAVILY_API_KEY`: 已有
- `REDDIT_CLIENT_ID`: 需要申请（免费）
- `REDDIT_CLIENT_SECRET`: 需要申请（免费）
- `OPENWEATHERMAP_API_KEY`: 需要申请（免费）
- `EXCHANGERATE_API_KEY`: 需要申请（免费）

---

## 2. 申请免费API Key（15分钟）

### Reddit API（免费，无限制）
1. 访问 https://www.reddit.com/prefs/apps
2. 登录Reddit账号
3. 点击"create another app..."
4. 选择"script"
5. 填写名称: `DeepFindAgent`
6. 填写描述: `Deep research agent for product analysis`
7. 点击"create app"
8. 复制`client_id`（在app名称下方）
9. 复制`client_secret`
10. 粘贴到`.env.local`

### OpenWeatherMap API（免费，1000次/天）
1. 访问 https://openweathermap.org/api
2. 注册账号（Sign Up）
3. 登录后，进入API keys页面
4. 复制默认的API Key
5. 粘贴到`.env.local`

### ExchangeRate API（免费，1500次/月）
1. 访问 https://www.exchangerate-api.com/
2. 注册账号（Sign Up Free）
3. 登录后，进入Dashboard
4. 复制API Key
5. 粘贴到`.env.local`

---

## 3. 验证环境（2分钟）

### 3.1 检查Python环境
```bash
cd /Users/purepure/Desktop/docs/deepfind-agent
source venv/bin/activate
python --version
# 应该输出: Python 3.9.x
```

### 3.2 检查依赖
```bash
pip list | grep praw
# 应该输出: praw 7.x.x
```

如果没有安装，执行：
```bash
pip install praw feedparser httpx
```

---

## 4. 快速测试（5分钟）

### 4.1 测试Reddit API
```bash
cd /Users/purepure/Desktop/docs/deepfind-agent
python -c "
import praw
reddit = praw.Reddit(
    client_id='your_client_id',
    client_secret='your_client_secret',
    user_agent='DeepFindAgent/1.0'
)
# 搜索iPhone 15 Pro相关帖子
for post in reddit.subreddit('all').search('iPhone 15 Pro review', limit=5):
    print(f'标题: {post.title}')
    print(f'点赞: {post.score}, 评论: {post.num_comments}')
    print('---')
"
```

### 4.2 测试Hacker News API
```bash
python -c "
import httpx
response = httpx.get('https://hn.algolia.com/api/v1/search?query=Claude+3')
data = response.json()
for hit in data['hits'][:5]:
    print(f'标题: {hit[\"title\"]}')
    print(f'点赞: {hit[\"points\"]}, 评论: {hit[\"num_comments\"]}')
    print('---')
"
```

### 4.3 测试Google News RSS
```bash
python -c "
import feedparser
rss_url = 'https://news.google.com/rss/search?q=人工智能&hl=zh-CN'
feed = feedparser.parse(rss_url)
for entry in feed.entries[:5]:
    print(f'标题: {entry.title}')
    print(f'来源: {entry.source.title}')
    print('---')
"
```

---

## 5. 启动服务（2分钟）

### 5.1 启动后端
```bash
cd /Users/purepure/Desktop/docs/deepfind-agent
source venv/bin/activate
python api.py

# 应该看到:
# INFO:     Started server process
# INFO:     Waiting for application startup.
# INFO:     Application startup complete.
# INFO:     Uvicorn running on http://0.0.0.0:8000
```

### 5.2 启动前端（另一个终端）
```bash
cd /Users/purepure/Desktop/docs/deepfind-agent/frontend
npm run dev

# 应该看到:
#   VITE v5.x.x  ready in xxx ms
#   ➜  Local:   http://localhost:3000/
```

### 5.3 访问前端
打开浏览器访问: http://localhost:3000

---

## 6. 测试查询（1分钟）

### 产品方案场景
```
查询: "分析iPhone 15 Pro和华为Mate 60 Pro的竞品对比，给出产品方案建议"
```

### 旅游攻略场景
```
查询: "纽约4天3晚旅行攻略"
```

### 行业洞察场景
```
查询: "Claude 3发布对AI行业的影响"
```

---

## 7. 查看测试输出

### 7.1 查看生成的报告
```bash
cd /Users/purepure/Desktop/docs/deepfind-agent/test/test_outputs/reports
ls -la
# 查看生成的报告文件
```

### 7.2 查看日志
```bash
cd /Users/purepure/Desktop/docs/deepfind-agent/test/test_outputs/logs
tail -f *.log
# 实时查看日志
```

---

## 8. 常见问题

### Q1: Reddit API报错"401 Unauthorized"
**原因**: client_id或client_secret错误
**解决**: 检查`.env.local`中的Reddit配置

### Q2: 搜索结果无数据
**原因**: API Key未配置或网络问题
**解决**: 检查网络连接和API Key配置

### Q3: 前端无法连接后端
**原因**: 后端未启动或端口错误
**解决**: 
```bash
# 检查后端是否启动
ps aux | grep api.py

# 检查端口是否占用
lsof -ti:8000

# 杀掉占用进程
lsof -ti:8000 | xargs kill -9
```

### Q4: Mac M1/M2芯片安装依赖失败
**解决**: 使用conda虚拟环境
```bash
conda create -n deepfind python=3.9
conda activate deepfind
pip install -r requirements.txt
```

---

## 9. 下一步

- [ ] 测试Reddit API
- [ ] 测试Hacker News API
- [ ] 测试Google News RSS
- [ ] 测试场景分类
- [ ] 测试报告生成
- [ ] 测试用户数据上传

---

**创建时间**: 2026-06-30
**维护者**: 本地开发环境