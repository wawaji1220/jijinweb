#!/bin/bash

set -e

echo "=== Django 基金管理系统 - Docker 启动脚本 ==="

# 等待数据库初始化
if [ ! -f "db/db.sqlite3" ]; then
    echo "数据库不存在，开始初始化..."
    mkdir -p db
fi

# 数据库迁移
echo "执行数据库迁移..."
python manage.py migrate --noinput

# 收集静态文件
echo "收集静态文件..."
python manage.py collectstatic --noinput

# 创建超级用户（如果不存在）
echo "检查超级用户..."
python -c "
import os
import django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'jijinweb.settings')
django.setup()
from django.contrib.auth import get_user_model
User = get_user_model()
if not User.objects.filter(is_superuser=True).exists():
    print('创建默认超级用户...')
    User.objects.create_superuser('admin', 'admin@example.com', 'admin123')
    print('默认管理员账号: admin / admin123')
else:
    print('超级用户已存在')
"

echo "=== 启动 Django 服务器和调度器 ==="

# 后台启动调度器
python manage.py start_scheduler &
PID_SCHEDULER=$!

# 启动 Django 开发服务器
python manage.py runserver 0.0.0.0:8000

# 等待调度器进程
wait $PID_SCHEDULER
