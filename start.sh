#!/bin/bash
echo "===================================="
echo "  基金净值实时估算系统 - 快速启动"
echo "===================================="
echo

echo "[1/5] 检查虚拟环境..."
if [ ! -d "venv" ]; then
    echo "虚拟环境不存在,正在创建..."
    python3 -m venv venv
    source venv/bin/activate
    echo "正在安装依赖..."
    pip install -r requirements.txt
else
    source venv/bin/activate
fi
echo "虚拟环境已激活"
echo

echo "[2/5] 检查数据库..."
if [ ! -f "db.sqlite3" ]; then
    echo "正在初始化数据库..."
    python manage.py makemigrations
    python manage.py migrate
    echo "超级用户: admin (请手动设置密码)"
else
    echo "数据库已存在"
fi
echo

echo "[3/5] 收集静态文件..."
python manage.py collectstatic --noinput
echo

echo "[4/5] 启动定时任务调度器..."
python scheduler.py &
SCHEDULER_PID=$!
echo "定时任务已启动 (PID: $SCHEDULER_PID)"
echo

echo "[5/5] 启动Django开发服务器..."
echo
echo "===================================="
echo " 访问地址: http://127.0.0.1:8000"
echo " 管理后台: http://127.0.0.1:8000/admin"
echo "===================================="
echo

python manage.py runserver

# 清理
kill $SCHEDULER_PID 2>/dev/null
