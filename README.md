# SearchAllNewsPlatform
一键可搜全网新闻（微博、头条、搜狐）并下载图片、视频、文字！开箱即用！保存的数据是json结构！采用的是DrissionPage方案，安装毫无压力，稳定性超高
注意：微博搜索需要登入，登入一次即可，后面就不用处理了

## 主要功能

- 支持多平台数据采集（微博、头条等）
- 自动解析文本内容、图片、视频等媒体数据
- 灵活的数据过滤机制
- 支持数据本地存储，支持JSON格式
- 自动下载和保存媒体文件

## 项目结构

```
├── search_weibo.py    # 微博数据采集模块
├── search_toutiao.py  # 头条数据采集模块
├── filter.py          # 数据过滤模块
├── storage.py         # 数据存储模块
├── util.py            # 工具函数模块
└── all_search.py      # 统一搜索入口
```

## 使用方法

### 1. 微博数据采集（单项目搜索）

```python
from search_weibo import WeiBoSearch

# 初始化搜索器
weibo = WeiBoSearch()

# 设置采集页数（默认是5页）
weibo.page_num = 2

# 执行搜索并保存数据
json_file = weibo.search_and_storage('关键词')
```

### 2. 全网搜索

```python
news = SearchNews()
news.page_num = 1
news.search_and_storage('赵丽颖')
```

### 3. 自定义数据过滤及存储

```python
# 定义筛选条件（不设置就不会筛选）
filter_options = FilterDataDict()
filter_options.limit_hours = 48  # 只选择48小时内的资讯

# 定义存储方案
storage_options = Storage()
storage_options.root = 'file_root'  # 定义根目录

weibo = WeiBoSearch(filter_options=filter_options, storage_options=storage_options)
weibo.page_num = 2
weibo.search_news('赵丽颖')
```

## 数据格式

采集的数据统一保存为JSON格式，包含以下字段：

```json
{
    "platform": "weibo",        # 平台名称
    "keyword": "搜索关键词",    # 搜索关键词
    "title": "",              # 标题
    "text": "正文内容",        # 文本内容
    "user": "用户名",         # 发布用户
    "userID": 123456,         # 用户ID
    "time_int": 1234567890,   # 发布时间戳
    "media_type": "img",      # 媒体类型（img/video）
    "media_list": [],         # 媒体文件列表
    "forward_num": 0,         # 转发数
    "comments_num": 0,        # 评论数
    "likes_num": 0           # 点赞数
}
```

## 注意事项

1. 微博数据采集需要登录账号，首次使用会自动打开浏览器等待登录
2. 为避免被封禁，采集过程中设置了随机等待时间
3. 建议合理设置采集页数，避免采集过多数据
4. 媒体文件会自动下载到本地存储

## 依赖安装

```bash
pip install -r requirements.txt
```
