# 基金净值实时估算系统

基于Django框架开发的中国基金净值实时估算网页应用。

## 功能特性

- ✅ 实时获取基金数据(新浪财经 + 东方财富网)
- ✅ 支持最新估值和实时涨跌显示
- ✅ 每30分钟自动刷新数据
- ✅ 基金净值走势可视化图表
- ✅ 支持基金代码和名称搜索
- ✅ 响应式设计,适配移动端和PC端
- ✅ 智能缓存机制优化性能
- ✅ 后台管理界面
- ✅ UTF-8编码支持,中文显示正常
- ✅ 点击基金卡片跳转新浪财经详情页

## 技术栈

- **后端**: Django 4.2
- **前端**: Bootstrap 5
- **图表**: Plotly.js
- **数据源**:
  - 新浪财经HQ API (最新估值、实时涨跌)
  - 东方财富网 (历史净值数据)
- **缓存**: Django Cache Framework (LocMem/Redis)
- **定时任务**: APScheduler

## 项目结构

```
jijinweb/
├── jijinweb/              # 项目主配置
│   ├── settings.py       # 配置文件
│   ├── urls.py           # URL配置
│   └── wsgi.py           # WSGI配置
├── funds/                # 基金应用
│   ├── models.py         # 数据模型
│   ├── views.py          # 视图函数(热门基金显示20个)
│   ├── urls.py           # URL路由
│   ├── admin.py          # 管理后台
│   ├── services/         # 业务服务
│   │   ├── fund_fetcher_real.py  # 数据获取(新浪+东方财富)
│   │   └── cache_manager.py      # 缓存管理
│   ├── utils/            # 工具类
│   │   └── chart_generator.py   # 图表生成
│   ├── tasks.py          # 异步任务
│   └── management/       # 管理命令
│       └── commands/
│           ├── fetch_fund_data.py  # 获取基金数据
│           ├── test_encoding.py    # 测试编码
│           └── test_sina.py        # 测试新浪API
├── templates/            # 模板文件
│   ├── base.html
│   └── funds/
│       ├── index.html    # 首页(20个热门基金)
│       ├── detail.html   # 详情页
│       └── search.html   # 搜索页
├── static/               # 静态文件
├── scheduler.py          # 定时任务调度器(30分钟刷新)
├── init_data.py          # 初始化基金数据脚本
├── requirements.txt      # 依赖包
├── start.bat/start.sh    # 快速启动脚本
└── manage.py            # Django管理脚本
```

## 数据源说明

### 新浪财经HQ API
- **用途**: 获取最新估值、实时涨跌、开盘净值
- **API URL**: `https://hq.sinajs.cn/list=fu_{基金代码}`
- **数据字段**: 基金名称、最新估值、估值涨跌%、开盘净值、累计净值、前一日净值、数据日期
- **编码**: GBK
- **刷新频率**: 实时

### 东方财富网API
- **用途**: 获取历史净值数据(用于图表展示)
- **数据字段**: 单位净值、累计净值、净值日期
- **备用**: 当新浪API失败时作为降级数据源

## 快速开始

### Windows 用户

#### 方法一: 使用快速启动脚本(推荐)

```cmd
# 双击运行 start.bat
start.bat
```

脚本会自动完成:
1. 创建并激活虚拟环境
2. 安装依赖
3. 初始化数据库
4. 创建超级用户(默认用户名: admin)
5. 启动定时任务
6. 启动Web服务

访问:
- 首页: http://127.0.0.1:8000
- 管理后台: http://127.0.0.1:8000/admin

#### 方法二: 手动启动

```cmd
# 1. 创建虚拟环境
python -m venv venv

# 2. 激活虚拟环境
venv\Scripts\activate

# 3. 安装依赖
pip install -r requirements.txt

# 4. 数据库迁移
python manage.py makemigrations
python manage.py migrate

# 5. 初始化基金数据
python init_data.py

# 6. 创建超级用户(可选)
python manage.py createsuperuser

# 7. 启动定时任务(新开一个终端)
python scheduler.py

# 8. 启动开发服务器
python manage.py runserver
```

### Linux/Mac 用户

#### 方法一: 使用快速启动脚本(推荐)

```bash
chmod +x start.sh
./start.sh
```

#### 方法二: 手动启动

```bash
# 1. 创建虚拟环境
python3 -m venv venv

# 2. 激活虚拟环境
source venv/bin/activate

# 3. 安装依赖
pip install -r requirements.txt

# 4. 数据库迁移
python manage.py makemigrations
python manage.py migrate

# 5. 初始化基金数据
python init_data.py

# 6. 创建超级用户(可选)
python manage.py createsuperuser

# 7. 启动定时任务(新开一个终端)
python scheduler.py

# 8. 启动开发服务器
python manage.py runserver
```

## 使用说明

### 首页功能

1. **热门基金展示**
   - 显示20只热门基金
   - 包含最新净值、估算涨跌
   - 点击卡片跳转新浪财经详情页(新标签页打开)

2. **搜索功能**
   - 支持基金代码搜索(如: 000001)
   - 支持基金名称搜索(如: 易方达)
   - 搜索结果分页显示

3. **实时刷新**
   - 数据每30分钟自动刷新
   - 点击"立即刷新"按钮可手动刷新
   - 显示最后更新时间

### 基金详情页

- 查看实时净值数据(最新估值、涨跌、开盘净值、累计净值)
- 查看净值走势图表(最近30天)
- 查看历史净值记录
- 跳转到新浪财经详情页

### 管理命令

#### 获取单个基金数据

```bash
python manage.py fetch_fund_data --code 000001
```

#### 获取所有基金数据

```bash
python manage.py fetch_fund_data --all
```

#### 获取基金历史数据

```bash
python manage.py fetch_fund_data --code 000001 --history
```

#### 初始化基金数据

```bash
python init_data.py            # 初始化热门基金
python init_data.py init       # 同上
python init_data.py clear      # 清空所有基金
```

#### 测试新浪API

```bash
python manage.py test_sina
```

#### 测试编码

```bash
python manage.py test_encoding
```

### 添加基金

#### 方式一: 使用管理后台

1. 访问 http://127.0.0.1:8000/admin
2. 登录超级用户账号
3. 进入 "基金" 管理
4. 添加新基金

#### 方式二: 使用Django Shell

```bash
python manage.py shell
```

```python
from funds.models import Fund

# 添加单个基金
Fund.objects.create(
    fund_code='000001',
    fund_name='华夏成长混合',
    fund_type='混合型',
    fund_company='华夏基金'
)

# 批量添加
funds_data = [
    ('000001', '华夏成长混合', '混合型', '华夏基金'),
    ('110022', '易方达消费行业股票', '股票型', '易方达基金'),
]

for code, name, ftype, company in funds_data:
    Fund.objects.get_or_create(
        fund_code=code,
        defaults={
            'fund_name': name,
            'fund_type': ftype,
            'fund_company': company
        }
    )
```

### API接口

#### 获取基金实时数据

```
GET /api/realtime/?code=000001
```

响应:

```json
{
    "success": true,
    "data": {
        "fund_code": "000001",
        "name": "华夏成长混合",
        "estimated_nav": "1.1250",
        "estimated_growth": "0.14",
        "unit_nav": "1.1234",
        "accumulated_nav": "3.4567",
        "nav_date": "2026-02-13",
        "prev_nav": "1.1230",
        "prev_nav_date": "2026-02-12"
    },
    "cached": false
}
```

#### 获取基金历史数据

```
GET /api/history/?code=000001&days=30
```

#### 搜索基金

```
GET /api/search/?q=易方达
```

## 数据字段说明

### 实时数据字段

| 字段 | 说明 | 数据来源 |
|------|------|----------|
| fund_code | 基金代码 | 数据库 |
| name | 基金名称 | 新浪/东方财富 |
| estimated_nav | 最新估值 | 新浪API |
| estimated_growth | 估算涨跌% | 新浪API |
| unit_nav | 今日开盘净值 | 新浪API |
| accumulated_nav | 累计净值 | 新浪API |
| nav_date | 数据日期 | 新浪API |
| prev_nav | 前一日净值 | 新浪API |
| prev_nav_date | 前一日净值日期 | 自动计算(nav_date前一日) |

### 历史数据字段

| 字段 | 说明 |
|------|------|
| nav_date | 净值日期 |
| unit_nav | 单位净值 |
| accumulated_nav | 累计净值 |
| daily_growth | 日增长率 |

## 缓存配置

### 使用内存缓存(默认)

已配置在 `settings.py` 中,适合开发环境。

### 使用Redis缓存(生产环境推荐)

1. 安装Redis并启动

2. 安装django-redis:

```bash
pip install django-redis
```

3. 修改 `settings.py` 中的缓存配置:

```python
CACHES = {
    'default': {
        'BACKEND': 'django_redis.cache.RedisCache',
        'LOCATION': 'redis://127.0.0.1:6379/1',
        'OPTIONS': {
            'CLIENT_CLASS': 'django_redis.client.DefaultClient',
        },
        'TIMEOUT': 300,
    }
}
```

## 修改刷新间隔

### 修改自动刷新间隔

编辑 `scheduler.py` 文件,修改定时任务的间隔:

```python
# 当前设置为30分钟
scheduler.add_job(fetch_all_funds, 'interval', minutes=30)
```

修改为其他值:
- `minutes=5` - 每5分钟刷新
- `hours=1` - 每小时刷新

### 修改前端自动刷新

编辑 `templates/funds/index.html`,修改JavaScript中的定时器:

```javascript
// 当前设置为30分钟
setInterval(refreshData, 1800000); // 30分钟 = 1800000毫秒
```

修改为其他值:
- `300000` - 5分钟
- `600000` - 10分钟

## 生产环境部署

### 使用Gunicorn

```bash
pip install gunicorn
gunicorn jijinweb.wsgi:application --bind 0.0.0.0:8000 --workers 4
```

### 使用Nginx反向代理

配置Nginx:

```nginx
server {
    listen 80;
    server_name your-domain.com;

    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
    }

    location /static/ {
        alias /path/to/jijinweb/staticfiles/;
    }

    location /media/ {
        alias /path/to/jijinweb/media/;
    }
}
```

### 使用Systemd管理服务

创建 `/etc/systemd/system/django-jijinweb.service`:

```ini
[Unit]
Description=Django Fund Web Application
After=network.target

[Service]
User=www-data
Group=www-data
WorkingDirectory=/path/to/jijinweb
ExecStart=/path/to/venv/bin/gunicorn jijinweb.wsgi:application --bind 127.0.0.1:8000 --workers 4
Restart=always

[Install]
WantedBy=multi-user.target
```

启动服务:

```bash
systemctl enable django-jijinweb
systemctl start django-jijinweb
```

## 常见问题

### Q: 数据不更新?

**A:**
1. 检查定时任务是否运行(`python scheduler.py`)
2. 检查网络连接
3. 点击"立即刷新"按钮
4. 查看日志是否有错误信息

### Q: 中文显示乱码?

**A:**
系统已修复UTF-8编码问题,如仍有问题:
1. 运行 `python manage.py test_encoding` 测试
2. 检查数据库编码是否为UTF-8
3. 清空数据重新初始化: `python init_data.py clear && python init_data.py`

### Q: 找不到基金?

**A:**
1. 使用基金代码精确搜索(如: 000001)
2. 尝试搜索基金名称关键词
3. 在管理后台手动添加基金
4. 检查数据源API是否正常

### Q: 图表不显示?

**A:**
1. 检查浏览器是否支持JavaScript
2. 检查网络连接(需要加载Plotly库)
3. 刷新页面重试

### Q: 如何修改首页显示的基金数量?

**A:**
编辑 `funds/views.py`,修改 `index` 函数:

```python
# 当前设置为20个
popular_funds = Fund.objects.all()[:20]
```

### Q: 新浪API返回403错误?

**A:**
系统已添加Referer头,如仍有问题:
1. 检查请求头配置
2. 确保能访问 https://finance.sina.com.cn
3. 运行 `python manage.py test_sina` 测试

## 注意事项

1. **数据源限制**: 新浪和东方财富API有访问频率限制,请合理设置刷新间隔
2. **缓存时间**: 实时数据默认缓存5分钟,历史数据缓存1小时
3. **网络依赖**: 应用需要能访问外网获取数据
4. **投资风险**: 本站数据仅供参考,不构成投资建议

## 性能优化建议

1. **生产环境使用Redis缓存**
   - 替换默认的LocMemCache
   - 提高并发处理能力

2. **使用Nginx反向代理**
   - 静态文件由Nginx直接服务
   - 提高响应速度

3. **使用Gunicorn部署**
   - 替换开发服务器
   - 多Worker进程处理请求

4. **配置CDN加速**
   - 静态资源使用CDN
   - 减少服务器压力

## 文档索引

- [安装指南](INSTALL.md) - Windows安装问题解决方案
- [快速入门](QUICKSTART.md) - 快速开始指南
- [新浪集成说明](SINA_INTEGRATION_SUMMARY.md) - 新浪API集成详情
- [编码修复说明](ENCODING_FIX_COMPLETED.md) - UTF-8编码修复
- [链接更新说明](LINK_UPDATE_SUMMARY.md) - 外部链接更新

## 许可证

MIT License

## 联系方式

如有问题或建议,欢迎提Issue。
