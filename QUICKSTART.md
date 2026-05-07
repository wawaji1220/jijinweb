# 快速入门指南

本指南将帮助您快速上手基金净值实时估算系统。

## 第一次使用

### Windows 用户

#### 快速启动(推荐)

1. 双击运行 `start.bat`
2. 等待自动安装和初始化完成
3. 浏览器访问: http://127.0.0.1:8000

#### 手动启动

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

#### 快速启动(推荐)

```bash
chmod +x start.sh
./start.sh
```

#### 手动启动

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

## 系统概览

### 首页

访问 http://127.0.0.1:8000

首页展示:
- **热门基金列表**: 显示20只热门基金
- **搜索框**: 支持基金代码和名称搜索
- **自动刷新提示**: 显示最后更新时间和刷新按钮
- **推荐基金**: 快速访问常用基金

### 基金详情页

点击任意基金卡片或搜索结果可进入详情页,查看:
- **实时数据**: 最新估值、估算涨跌、开盘净值、累计净值
- **净值走势图**: 交互式图表,显示最近30天的净值变化
- **历史净值记录**: 详细的历史净值数据表
- **新浪链接**: 点击跳转到新浪财经详情页

### 管理后台

访问 http://127.0.0.1:8000/admin

使用超级用户登录后可以:
- **管理基金**: 添加、编辑、删除基金
- **管理净值记录**: 查看和管理历史净值数据
- **用户管理**: 管理系统用户

## 常用操作

### 添加基金

#### 方法1: 使用管理后台

1. 访问 http://127.0.0.1:8000/admin
2. 登录超级用户账号
3. 点击 "基金" -> "增加"
4. 填写基金信息:
   - 基金代码: 如 000001
   - 基金名称: 如 华夏成长混合
   - 基金类型: 如 混合型
   - 基金公司: 如 华夏基金
5. 点击"保存"

#### 方法2: 使用Django Shell

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
    ('000961', '天弘沪深300ETF联接A', '指数型', '天弘基金'),
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

# 退出Shell
exit()
```

### 搜索基金

1. 在首页搜索框中输入:
   - 基金代码: `000001`
   - 基金名称关键词: `易方达` 或 `消费`

2. 点击"搜索"按钮

3. 查看搜索结果,支持分页

### 手动刷新数据

#### 方法1: 使用首页刷新按钮

在首页点击"立即刷新"按钮,刷新所有热门基金数据。

#### 方法2: 使用管理命令

```bash
# 获取单个基金数据
python manage.py fetch_fund_data --code 000001

# 获取所有基金数据
python manage.py fetch_fund_data --all

# 获取历史数据
python manage.py fetch_fund_data --code 000001 --history
```

### 初始化基金数据

```bash
# 初始化热门基金
python init_data.py

# 清空所有基金
python init_data.py clear

# 重新初始化
python init_data.py clear
python init_data.py
```

## 数据说明

### 实时数据字段

| 字段 | 说明 | 示例 |
|------|------|------|
| 最新估值 | 当日实时估算净值 | 1.4454 |
| 估算涨跌 | 相对于前一交易日的涨跌幅 | +0.14% 或 -0.39% |
| 开盘净值 | 今日开盘净值 | 1.3600 |
| 累计净值 | 基金成立以来累计净值 | 3.4567 |
| 前一日净值 | 前一交易日净值 | 1.4400 |
| 数据日期 | 数据对应的日期 | 2026-02-13 |

### 涨跌颜色说明

- **红色**: 上涨 (如 +0.14%)
- **绿色**: 下跌 (如 -0.39%)
- **灰色**: 无数据

## 自定义配置

### 修改首页显示基金数量

编辑 `funds/views.py`,修改 `index` 函数:

```python
# 当前设置为20个
popular_funds = Fund.objects.all()[:20]
```

修改为其他数量,如10个:

```python
popular_funds = Fund.objects.all()[:10]
```

### 修改自动刷新间隔

#### 后端刷新间隔

编辑 `scheduler.py`:

```python
# 当前设置为30分钟
scheduler.add_job(fetch_all_funds, 'interval', minutes=30)
```

修改为其他值:
- `minutes=5` - 每5分钟
- `minutes=10` - 每10分钟
- `hours=1` - 每小时

#### 前端自动刷新

编辑 `templates/funds/index.html`:

```javascript
// 当前设置为30分钟
setInterval(refreshData, 1800000); // 30分钟 = 1800000毫秒
```

修改为其他值:
- `300000` - 5分钟
- `600000` - 10分钟
- `3600000` - 1小时

### 修改推荐的基金

编辑 `templates/funds/index.html`,找到推荐基金部分:

```html
<!-- 推荐基金 -->
<div class="col-md-4 mb-2">
    <a href="https://finance.sina.com.cn/fund/quotes/000001/bc.shtml" target="_blank" class="btn btn-outline-primary btn-sm">000001 华夏成长混合</a>
</div>
```

添加或修改推荐基金链接。

## 常见问题

### Q: 数据不更新?

**A:**
1. 检查定时任务是否运行(需要有终端运行 `python scheduler.py`)
2. 检查网络连接
3. 点击首页"立即刷新"按钮
4. 查看终端是否有错误信息

### Q: 中文显示乱码?

**A:**
系统已修复UTF-8编码问题,如仍有问题:
```bash
# 测试编码
python manage.py test_encoding

# 清空数据重新初始化
python init_data.py clear
python init_data.py
```

### Q: 找不到某个基金?

**A:**
1. 使用6位基金代码精确搜索
2. 尝试搜索基金名称关键词
3. 在管理后台手动添加基金
4. 确认基金代码是否正确

### Q: 图表不显示?

**A:**
1. 检查浏览器是否支持JavaScript
2. 检查网络连接(需要加载Plotly库)
3. 刷新页面重试
4. 尝试使用Chrome或Edge浏览器

### Q: 如何使用手机访问?

**A:**
1. 确保手机和电脑在同一局域网
2. 查看电脑IP地址(Windows: `ipconfig`, Linux/Mac: `ifconfig`)
3. 在手机浏览器访问: `http://电脑IP:8000`
4. 如果无法访问,可能需要关闭防火墙

### Q: 如何导出基金数据?

**A:**
```bash
python manage.py shell
```

```python
from funds.models import Fund
import csv

# 导出基金列表
with open('funds.csv', 'w', newline='', encoding='utf-8-sig') as f:
    writer = csv.writer(f)
    writer.writerow(['基金代码', '基金名称', '基金类型', '基金公司'])
    for fund in Fund.objects.all():
        writer.writerow([
            fund.fund_code,
            fund.fund_name,
            fund.fund_type,
            fund.fund_company
        ])

exit()
```

## 性能优化

### 使用Redis缓存(生产环境推荐)

```bash
# 安装Redis和django-redis
pip install django-redis

# 修改 settings.py 中的CACHES配置
```

详细配置请参考 [README.md](README.md)

## 开发调试

### 查看日志

在 `settings.py` 中添加日志配置:

```python
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'handlers': {
        'file': {
            'level': 'INFO',
            'class': 'logging.FileHandler',
            'filename': 'debug.log',
        },
    },
    'loggers': {
        'django': {
            'handlers': ['file'],
            'level': 'INFO',
            'propagate': True,
        },
        'funds': {
            'handlers': ['file'],
            'level': 'INFO',
            'propagate': True,
        },
    },
}
```

### VSCode调试

项目已配置好 `launch.json`,可以直接:
1. 打开VSCode
2. 按F5启动调试
3. 选择 "Django: Run Server" 或 "Django: Debug Server"

## 下一步

- 📖 阅读 [README.md](README.md) 了解更多细节
- 🚀 学习 [生产环境部署](README.md#生产环境部署)
- 🎨 自定义前端样式(修改 `static/` 目录下的CSS)
- 📊 添加更多数据分析功能
- 🔔 添加价格预警功能

## 技术支持

如有问题,请查看:
1. [README.md](README.md) - 完整文档
2. [INSTALL.md](INSTALL.md) - 安装指南
3. [TROUBLESHOOTING.md](TROUBLESHOOTING.md) - 故障排除
4. Django官方文档: https://docs.djangoproject.com/

---

祝您使用愉快! 🎉
