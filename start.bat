@echo off
chcp 65001 >nul
echo ====================================
echo   基金净值实时估算系统 - 快速启动
echo ====================================
echo.

echo [1/5] 检查虚拟环境...
if not exist "venv\Scripts\activate.bat" (
    echo 虚拟环境不存在,正在创建...
    python -m venv venv
    call venv\Scripts\activate.bat
    echo 正在安装依赖...
    pip install -r requirements.txt
) else (
    call venv\Scripts\activate.bat
)
echo 虚拟环境已激活
echo.

echo [2/5] 检查数据库...
if not exist "db.sqlite3" (
    echo 正在初始化数据库...
    python manage.py makemigrations
    python manage.py migrate
    python manage.py createsuperuser --noinput --username admin --email admin@example.com 2>nul || echo 超级用户已存在
) else (
    echo 数据库已存在
)
echo.

echo [3/5] 收集静态文件...
python manage.py collectstatic --noinput
echo.

echo [4/5] 启动定时任务调度器...
start "Fund Scheduler" cmd /k "python scheduler.py"
echo 定时任务已启动
echo.

echo [5/5] 启动Django开发服务器...
echo.
echo ====================================
echo  访问地址: http://127.0.0.1:8000
echo  管理后台: http://127.0.0.1:8000/admin
echo  用户名: admin (默认)
echo  密码: (首次运行需要设置)
echo ====================================
echo.

python manage.py runserver

pause
