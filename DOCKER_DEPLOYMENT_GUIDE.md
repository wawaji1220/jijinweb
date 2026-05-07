# Django 基金管理系统 Docker 部署指南

## 目录

- [系统要求](#系统要求)
- [快速开始](#快速开始)
- [详细配置](#详细配置)
- [常用命令](#常用命令)
- [生产环境部署](#生产环境部署)
- [故障排查](#故障排查)
- [备份与恢复](#备份与恢复)
- [性能优化](#性能优化)

---

## 系统要求

### 硬件要求

- CPU: 2 核心及以上
- 内存: 4GB 及以上
- 硬盘: 10GB 可用空间

### 软件要求

- Docker: 20.10.0 及以上
- Docker Compose: 2.0.0 及以上

### 检查 Docker 安装

```bash
# 检查 Docker 版本
docker --version

# 检查 Docker Compose 版本
docker compose version

# 检查 Docker 是否运行
docker info
```

---

## 快速开始

### 1. 克隆或进入项目目录

```bash
cd d:\share\Develop\jijinweb
```

### 2. 创建环境变量文件

```bash
# Windows
copy .env.example .env

# Linux/Mac
cp .env.example .env
```

### 3. 修改 .env 文件（可选）

编辑 `.env` 文件，根据需要修改配置：

```env
# Django 配置
DJANGO_DEBUG=True
DJANGO_SECRET_KEY=change-this-to-a-random-secret-key-in-production
DJANGO_ALLOWED_HOSTS=localhost,127.0.0.1

# 超级用户配置
DJANGO_SUPERUSER_USERNAME=admin
DJANGO_SUPERUSER_EMAIL=admin@example.com
DJANGO_SUPERUSER_PASSWORD=admin123

# 时区设置
TZ=Asia/Shanghai
```

### 4. 构建并启动容器

```bash
# 构建镜像并启动服务
docker compose up -d --build

# 或者分步执行
# 先构建镜像
docker compose build

# 再启动服务
docker compose up -d
```

### 5. 查看启动日志

```bash
# 查看 Web 服务日志
docker compose logs -f web

# 查看 Scheduler 服务日志
docker compose logs -f scheduler

# 查看所有服务日志
docker compose logs -f
```

### 6. 访问应用

打开浏览器访问：http://localhost:8000

**默认管理员账号：**
- 用户名：`admin`
- 密码：`admin123`

首次启动后，建议立即修改默认密码！

---

## 详细配置

### 环境变量说明

| 变量名 | 默认值 | 说明 |
|--------|--------|------|
| `DJANGO_DEBUG` | `True` | 是否启用调试模式，生产环境设置为 `False` |
| `DJANGO_SECRET_KEY` | - | Django 密钥，生产环境必须修改为随机字符串 |
| `DJANGO_ALLOWED_HOSTS` | `localhost,127.0.0.1` | 允许访问的主机列表，逗号分隔 |
| `DJANGO_SUPERUSER_USERNAME` | `admin` | 超级用户名 |
| `DJANGO_SUPERUSER_EMAIL` | `admin@example.com` | 超级用户邮箱 |
| `DJANGO_SUPERUSER_PASSWORD` | `admin123` | 超级用户密码 |
| `TZ` | `Asia/Shanghai` | 时区设置 |

### 生成安全的 SECRET_KEY

```python
# 在 Python 中生成
import secrets
print(secrets.token_urlsafe(50))

# 或使用 Django 工具
python -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"
```

### Docker Compose 服务说明

#### Web 服务

```yaml
web:
  ports:
    - "8000:8000"      # 端口映射：主机8000 -> 容器8000
  volumes:
    - ./db:/app/db      # 数据库持久化
    - ./logs:/app/logs  # 日志持久化
    - ./media:/app/media  # 媒体文件持久化
    - .:/app            # 代码热重载（开发环境）
```

#### Scheduler 服务

```yaml
scheduler:
  command: python scheduler.py  # 定时任务命令
  depends_on:
    - web  # 依赖 Web 服务
```

### 修改端口映射

如果 8000 端口被占用，可以修改 `docker-compose.yml`：

```yaml
ports:
  - "8080:8000"  # 使用 8080 端口访问
```

修改后重启服务：

```bash
docker compose down
docker compose up -d
```

---

## 常用命令

### 容器管理

```bash
# 启动服务
docker compose up -d

# 停止服务
docker compose stop

# 重启服务
docker compose restart

# 停止并删除容器
docker compose down

# 停止并删除容器及数据卷
docker compose down -v

# 重新构建镜像
docker compose build

# 强制重新构建（不使用缓存）
docker compose build --no-cache
```

### 日志管理

```bash
# 查看实时日志
docker compose logs -f

# 查看最近 100 行日志
docker compose logs --tail=100

# 查看特定服务日志
docker compose logs -f web
docker compose logs -f scheduler

# 查看特定时间的日志
docker compose logs --since=2024-01-01T00:00:00
```

### 数据库管理

```bash
# 执行数据库迁移
docker compose exec web python manage.py migrate

# 创建超级用户
docker compose exec web python manage.py createsuperuser

# 进入 Django Shell
docker compose exec web python manage.py shell

# 备份数据库
docker compose exec web sqlite3 db/db.sqlite3 ".backup /app/db/backup_$(date +%Y%m%d).db"

# 查看数据库表
docker compose exec web python manage.py showmigrations
```

### 进入容器

```bash
# 进入 Web 容器
docker compose exec web bash

# 进入 Scheduler 容器
docker compose exec scheduler bash
```

### 更新代码

```bash
# 1. 拉取最新代码
git pull

# 2. 重新构建并启动
docker compose up -d --build

# 3. 执行数据库迁移（如果有）
docker compose exec web python manage.py migrate
```

---

## 生产环境部署

### 1. 修改环境变量

编辑 `.env` 文件：

```env
# 关闭调试模式
DJANGO_DEBUG=False

# 修改为真实的 SECRET_KEY
DJANGO_SECRET_KEY=your-random-secret-key-here

# 设置允许访问的主机
DJANGO_ALLOWED_HOSTS=yourdomain.com,www.yourdomain.com
```

### 2. 使用 Gunicorn 代替 runserver

创建 `gunicorn.conf.py`：

```python
bind = "0.0.0.0:8000"
workers = 4
worker_class = "sync"
worker_connections = 1000
max_requests = 1000
max_requests_jitter = 100
timeout = 30
keepalive = 5
```

修改 `docker-compose.yml` 的 Web 服务：

```yaml
web:
  command: gunicorn jijinweb.wsgi:application -c gunicorn.conf.py
```

### 3. 配置 Nginx 反向代理

创建 `nginx.conf`：

```nginx
events {
    worker_connections 1024;
}

http {
    upstream django {
        server web:8000;
    }

    server {
        listen 80;
        server_name yourdomain.com;

        client_max_body_size 20M;

        location /static/ {
            alias /app/staticfiles/;
        }

        location /media/ {
            alias /app/media/;
        }

        location / {
            proxy_pass http://django;
            proxy_set_header Host $host;
            proxy_set_header X-Real-IP $remote_addr;
            proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
            proxy_set_header X-Forwarded-Proto $scheme;
        }
    }
}
```

修改 `docker-compose.yml`，添加 Nginx 服务：

```yaml
services:
  web:
    # ... 配置不变

  nginx:
    image: nginx:alpine
    ports:
      - "80:80"
      - "443:443"
    volumes:
      - ./nginx.conf:/etc/nginx/nginx.conf
      - ./static:/app/staticfiles
      - ./media:/app/media
    depends_on:
      - web
    restart: unless-stopped
```

### 4. 配置 HTTPS（使用 Let's Encrypt）

```bash
# 安装 Certbot
docker run -it --rm \
  -v /etc/letsencrypt:/etc/letsencrypt \
  -v /var/lib/letsencrypt:/var/lib/letsencrypt \
  certbot/certbot certonly --standalone -d yourdomain.com
```

修改 `nginx.conf`：

```nginx
server {
    listen 443 ssl http2;
    server_name yourdomain.com;

    ssl_certificate /etc/letsencrypt/live/yourdomain.com/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/yourdomain.com/privkey.pem;

    # ... 其他配置
}

server {
    listen 80;
    server_name yourdomain.com;
    return 301 https://$server_name$request_uri;
}
```

### 5. 使用 PostgreSQL 替代 SQLite

修改 `.env`：

```env
DATABASE_URL=postgresql://user:password@postgres:5432/jijinweb
POSTGRES_DB=jijinweb
POSTGRES_USER=jijinuser
POSTGRES_PASSWORD=your-password
```

修改 `docker-compose.yml`：

```yaml
services:
  postgres:
    image: postgres:15-alpine
    environment:
      POSTGRES_DB: ${POSTGRES_DB}
      POSTGRES_USER: ${POSTGRES_USER}
      POSTGRES_PASSWORD: ${POSTGRES_PASSWORD}
    volumes:
      - postgres_data:/var/lib/postgresql/data
    restart: unless-stopped

  web:
    depends_on:
      - postgres

volumes:
  postgres_data:
```

### 6. 配置 Redis 缓存和 Celery

添加到 `requirements.txt`：

```
redis==5.0.1
celery==5.3.4
django-redis==5.4.0
```

修改 `docker-compose.yml`：

```yaml
services:
  redis:
    image: redis:7-alpine
    restart: unless-stopped

  celery:
    build: .
    command: celery -A jijinweb worker -l info
    depends_on:
      - redis
    volumes:
      - .:/app
    restart: unless-stopped

  celery-beat:
    build: .
    command: celery -A jijinweb beat -l info
    depends_on:
      - redis
    volumes:
      - .:/app
    restart: unless-stopped
```

---

## 故障排查

### 问题 1：容器启动失败

**症状：**
```bash
ERROR: for jijinweb  Cannot start service web: ...
```

**解决方案：**

```bash
# 查看详细错误日志
docker compose logs web

# 检查端口是否被占用
netstat -ano | findstr :8000  # Windows
lsof -i :8000  # Linux/Mac

# 清理并重新构建
docker compose down
docker compose build --no-cache
docker compose up -d
```

### 问题 2：数据库锁定错误

**症状：**
```
sqlite3.OperationalError: database is locked
```

**解决方案：**

1. 确保只有一个容器在写入数据库
2. 增加数据库超时时间，修改 `settings.py`：

```python
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db' / 'db.sqlite3',
        'OPTIONS': {
            'timeout': 20,  # 增加超时时间
        },
    }
}
```

3. 生产环境建议使用 PostgreSQL

### 问题 3：静态文件无法加载

**症状：**
页面样式丢失，控制台 404 错误

**解决方案：**

```bash
# 重新收集静态文件
docker compose exec web python manage.py collectstatic --noinput

# 检查 staticfiles 目录权限
docker compose exec web ls -la staticfiles/

# 确认 STATIC_ROOT 配置正确
```

### 问题 4：容器内存不足

**症状：**
容器频繁重启，日志显示 `OOMKilled`

**解决方案：**

修改 `docker-compose.yml`，限制资源使用：

```yaml
services:
  web:
    deploy:
      resources:
        limits:
          memory: 2G
        reservations:
          memory: 512M
```

### 问题 5：定时任务不执行

**症状：**
基金数据不更新

**解决方案：**

```bash
# 检查 scheduler 服务状态
docker compose ps

# 查看 scheduler 日志
docker compose logs -f scheduler

# 手动执行定时任务测试
docker compose exec scheduler python -c "
from funds.services.fund_fetcher_real import fetch_and_save_all_funds
fetch_and_save_all_funds()
"
```

### 问题 6：容器时间不正确

**症状：**
定时任务时间错误

**解决方案：**

确保 `.env` 文件中设置了正确的时区：

```env
TZ=Asia/Shanghai
```

或在 `docker-compose.yml` 中添加：

```yaml
environment:
  - TZ=Asia/Shanghai
```

### 问题 7：容器无法访问外部网络

**症状：**
基金数据抓取失败

**解决方案：**

```bash
# 检查容器网络连接
docker compose exec web ping -c 4 8.8.8.8

# 检查 DNS 配置
docker compose exec web cat /etc/resolv.conf

# 如果需要，修改 DNS
docker compose exec web sh -c "echo 'nameserver 8.8.8.8' >> /etc/resolv.conf"
```

---

## 备份与恢复

### 数据库备份

```bash
# 创建备份目录
mkdir -p backups

# 备份数据库
docker compose exec web sqlite3 db/db.sqlite3 ".backup /app/db/backup_$(date +%Y%m%d_%H%M%S).db"

# 复制备份到主机
docker cp jijinweb:/app/db/backup_20240101_120000.db ./backups/
```

### 自动备份脚本

创建 `backup.sh`：

```bash
#!/bin/bash

BACKUP_DIR="./backups"
DATE=$(date +%Y%m%d_%H%M%S)

mkdir -p $BACKUP_DIR

# 备份数据库
docker compose exec -T web sqlite3 db/db.sqlite3 ".backup /app/db/backup_${DATE}.db"
docker cp jijinweb:/app/db/backup_${DATE}.db $BACKUP_DIR/

# 备份媒体文件
docker cp jijinweb:/app/media $BACKUP_DIR/media_${DATE}

# 保留最近 7 天的备份
find $BACKUP_DIR -name "backup_*.db" -mtime +7 -delete

echo "备份完成: backup_${DATE}.db"
```

设置定时任务（Linux/Mac）：

```bash
# 编辑 crontab
crontab -e

# 每天凌晨 2 点备份
0 2 * * * /path/to/backup.sh >> /var/log/jijinweb_backup.log 2>&1
```

### 数据库恢复

```bash
# 停止服务
docker-compose stop

# 复制备份文件到容器
docker cp ./backups/backup_20240101_120000.db jijinweb:/app/db/db.sqlite3

# 启动服务
docker-compose start
```

### 完整备份（包括配置和代码）

```bash
#!/bin/bash

BACKUP_DIR="./backups"
DATE=$(date +%Y%m%d_%H%M%S)

mkdir -p $BACKUP_DIR

# 创建完整备份
tar -czf $BACKUP_DIR/complete_backup_${DATE}.tar.gz \
    --exclude='__pycache__' \
    --exclude='*.pyc' \
    --exclude='*.pyo' \
    --exclude='*.db' \
    --exclude='.git' \
    --exclude='backups' \
    .

# 备份数据库
docker compose exec -T web sqlite3 db/db.sqlite3 ".backup /app/db/backup_${DATE}.db"
docker cp jijinweb:/app/db/backup_${DATE}.db $BACKUP_DIR/

echo "完整备份完成: complete_backup_${DATE}.tar.gz"
```

---

## 性能优化

### 1. 减小镜像大小

优化 `Dockerfile`：

```dockerfile
# 多阶段构建
FROM python:3.11-slim as builder

WORKDIR /app

COPY requirements.txt .
RUN pip install --user --no-cache-dir -r requirements.txt

FROM python:3.11-slim

WORKDIR /app

# 只复制必要的文件
COPY --from=builder /root/.local /root/.local
COPY jijinweb/ ./jijinweb/
COPY funds/ ./funds/
COPY templates/ ./templates/
COPY manage.py .

ENV PATH=/root/.local/bin:$PATH

CMD ["gunicorn", "jijinweb.wsgi:application", "-b", "0.0.0.0:8000"]
```

### 2. 使用缓存层

```yaml
services:
  redis:
    image: redis:7-alpine
    volumes:
      - redis_data:/data
    restart: unless-stopped

volumes:
  redis_data:
```

在 `settings.py` 中配置：

```python
CACHES = {
    'default': {
        'BACKEND': 'django_redis.cache.RedisCache',
        'LOCATION': 'redis://redis:6379/1',
        'OPTIONS': {
            'CLIENT_CLASS': 'django_redis.client.DefaultClient',
        },
        'TIMEOUT': 300,
    }
}
```

### 3. 数据库优化

```python
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db' / 'db.sqlite3',
        'OPTIONS': {
            'timeout': 20,
            'check_same_thread': False,
        },
        'CONN_MAX_AGE': 60,  # 连接池
    }
}
```

### 4. 启用压缩

在 `settings.py` 中添加：

```python
MIDDLEWARE = [
    # ...
    'django.middleware.gzip.GZipMiddleware',
    # ...
]
```

### 5. 静态文件 CDN

在生产环境中，将静态文件上传到 CDN：

```bash
# 安装 django-storages
pip install django-storages boto3

# 在 settings.py 中配置
AWS_ACCESS_KEY_ID = 'your-access-key'
AWS_SECRET_ACCESS_KEY = 'your-secret-key'
AWS_STORAGE_BUCKET_NAME = 'your-bucket-name'
AWS_S3_REGION_NAME = 'your-region'

STATICFILES_STORAGE = 'storages.backends.s3boto3.S3Boto3Storage'
```

### 6. 数据库连接池

使用 `django-db-geventpool` 或 `django-db-connection-pool`：

```bash
pip install django-db-connection-pool
```

在 `settings.py` 中：

```python
DATABASE_POOL_ARGS = {
    'max_overflow': 10,
    'pool_size': 5,
    'recycle': 3600,
}
```

### 7. 启用监控

添加监控服务到 `docker-compose.yml`：

```yaml
services:
  prometheus:
    image: prom/prometheus
    ports:
      - "9090:9090"
    volumes:
      - ./prometheus.yml:/etc/prometheus/prometheus.yml

  grafana:
    image: grafana/grafana
    ports:
      - "3000:3000"
    environment:
      - GF_SECURITY_ADMIN_PASSWORD=admin
    volumes:
      - grafana_data:/var/lib/grafana

volumes:
  grafana_data:
```

---

## 安全建议

### 1. 限制容器权限

```yaml
services:
  web:
    security_opt:
      - no-new-privileges:true
    read_only: false  # 根据需要设置
    user: "1000:1000"
```

### 2. 网络隔离

```yaml
networks:
  frontend:
    external: true
  backend:
    internal: true

services:
  web:
    networks:
      - frontend
      - backend

  postgres:
    networks:
      - backend
```

### 3. 定期更新

```bash
# 检查基础镜像更新
docker pull python:3.11-slim

# 更新依赖包
pip list --outdated
pip install --upgrade package_name
```

### 4. 日志管理

```yaml
services:
  web:
    logging:
      driver: "json-file"
      options:
        max-size: "10m"
        max-file: "3"
```

### 5. 健康检查

```yaml
services:
  web:
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:8000/"]
      interval: 30s
      timeout: 10s
      retries: 3
      start_period: 40s
```

---

## 附录

### A. Docker Compose 命令速查表

| 命令 | 说明 |
|------|------|
| `docker-compose up -d` | 后台启动服务 |
| `docker-compose down` | 停止并删除容器 |
| `docker-compose stop` | 停止服务 |
| `docker-compose start` | 启动已停止的服务 |
| `docker-compose restart` | 重启服务 |
| `docker-compose ps` | 查看服务状态 |
| `docker-compose logs` | 查看日志 |
| `docker-compose build` | 构建镜像 |
| `docker-compose exec` | 在运行的容器中执行命令 |
| `docker-compose pull` | 拉取镜像 |

### B. 常用端口

| 服务 | 默认端口 | 说明 |
|------|----------|------|
| Django Web | 8000 | Web 服务 |
| Nginx | 80, 443 | 反向代理 |
| PostgreSQL | 5432 | 数据库 |
| Redis | 6379 | 缓存 |
| Grafana | 3000 | 监控面板 |
| Prometheus | 9090 | 指标采集 |

### C. 文件目录结构

```
jijinweb/
├── Dockerfile                  # Docker 镜像构建文件
├── docker-compose.yml          # Docker Compose 配置
├── .dockerignore               # Docker 构建忽略文件
├── docker-start.sh             # 容器启动脚本
├── .env                        # 环境变量（需创建）
├── .env.example                # 环境变量示例
├── requirements.txt            # Python 依赖
├── manage.py                   # Django 管理脚本
├── scheduler.py                # 定时任务脚本
├── jijinweb/                   # Django 项目配置
│   ├── settings.py             # Django 设置
│   ├── urls.py                 # URL 配置
│   └── wsgi.py                 # WSGI 配置
├── funds/                      # 基金应用
│   ├── models.py               # 数据模型
│   ├── views.py                # 视图函数
│   └── services/               # 业务逻辑
├── templates/                  # 模板文件
├── static/                     # 静态文件
├── media/                      # 媒体文件
├── db/                         # 数据库文件（持久化）
├── logs/                       # 日志文件（持久化）
└── backups/                    # 备份文件
```

### D. 常用链接

- Django 官方文档: https://docs.djangoproject.com/
- Docker 官方文档: https://docs.docker.com/
- Docker Compose 文档: https://docs.docker.com/compose/
- Gunicorn 文档: https://docs.gunicorn.org/

---

## 获取帮助

如果遇到问题：

1. 查看本文档的 [故障排查](#故障排查) 章节
2. 查看容器日志：`docker compose logs -f`
3. 检查 Django 官方文档
4. 在项目 GitHub Issues 提问

---

**最后更新：** 2024-01-01
