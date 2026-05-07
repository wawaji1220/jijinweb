# 安装指南

## 环境要求

- Python 3.8+
- pip (Python包管理器)
- 虚拟环境工具 venv

## Windows 安装

### 快速安装(推荐)

双击运行 `start.bat` 脚本即可自动完成所有安装步骤。

### 手动安装

#### 1. 创建虚拟环境

```cmd
python -m venv venv
```

#### 2. 激活虚拟环境

```cmd
venv\Scripts\activate
```

激活成功后,命令行前会显示 `(venv)`。

#### 3. 安装依赖

```cmd
pip install -r requirements.txt
```

如果安装依赖时遇到问题,参考下面的"常见安装问题"。

#### 4. 数据库迁移

```cmd
python manage.py makemigrations
python manage.py migrate
```

#### 5. 初始化基金数据

```cmd
python init_data.py
```

#### 6. 创建超级用户(可选)

```cmd
python manage.py createsuperuser
```

按照提示输入用户名、邮箱和密码。

#### 7. 启动应用

```cmd
# 终端1: 启动定时任务
python scheduler.py

# 终端2: 启动Web服务
python manage.py runserver
```

访问 http://127.0.0.1:8000

## Linux/Mac 安装

### 快速安装(推荐)

```bash
chmod +x start.sh
./start.sh
```

### 手动安装

#### 1. 创建虚拟环境

```bash
python3 -m venv venv
```

#### 2. 激活虚拟环境

```bash
source venv/bin/activate
```

#### 3. 安装依赖

```bash
pip install -r requirements.txt
```

#### 4. 数据库迁移

```bash
python manage.py makemigrations
python manage.py migrate
```

#### 5. 初始化基金数据

```bash
python init_data.py
```

#### 6. 创建超级用户(可选)

```bash
python manage.py createsuperuser
```

#### 7. 启动应用

```bash
# 终端1: 启动定时任务
python scheduler.py

# 终端2: 启动Web服务
python manage.py runserver
```

访问 http://127.0.0.1:8000

## 常见安装问题

### 问题1: pip版本过低

**症状**: 安装依赖时报错提示pip版本过低

**解决**:

```cmd
python -m pip install --upgrade pip
```

### 问题2: 网络连接超时

**症状**: 安装依赖时出现超时错误

**解决**: 使用国内镜像源

```cmd
# Windows
pip install -r requirements.txt -i https://pypi.tuna.tsinghua.edu.cn/simple

# Linux/Mac
pip install -r requirements.txt -i https://mirrors.aliyun.com/pypi/simple/
```

其他可选镜像源:
- 清华大学: `https://pypi.tuna.tsinghua.edu.cn/simple`
- 阿里云: `https://mirrors.aliyun.com/pypi/simple/`
- 中国科学技术大学: `https://pypi.mirrors.ustc.edu.cn/simple/`

### 问题3: 权限错误(Windows)

**症状**: 安装时出现权限错误

**解决**: 以管理员身份运行命令提示符

### 问题4: 权限错误(Linux/Mac)

**症状**: 安装时出现Permission denied错误

**解决**: 使用用户模式安装

```bash
pip install --user -r requirements.txt
```

### 问题5: Django安装失败

**症状**: Django安装报错

**解决**:

```cmd
# 先升级setuptools和wheel
pip install --upgrade setuptools wheel

# 然后安装Django
pip install Django==4.2.7
```

### 问题6: requests安装失败

**症状**: requests安装报错

**解决**:

```cmd
pip install requests==2.31.0
```

### 问题7: beautifulsoup4安装失败

**症状**: beautifulsoup4安装报错

**解决**:

```cmd
pip install beautifulsoup4==4.12.2
```

### 问题8: APScheduler安装失败

**症状**: APScheduler安装报错

**解决**:

```cmd
pip install APScheduler==3.10.4
```

### 问题9: plotly安装失败

**症状**: plotly安装报错

**解决**:

```cmd
pip install plotly==5.18.0
```

### 问题10: 数据库迁移失败

**症状**: 运行 `python manage.py migrate` 报错

**解决**:

```cmd
# 删除数据库文件
del db.sqlite3  # Windows
# 或
rm db.sqlite3   # Linux/Mac

# 删除迁移文件(保留__init__.py)
# Windows
rmdir /s /q funds\migrations\__pycache__
del funds\migrations\00*.py

# Linux/Mac
rm -rf funds/migrations/__pycache__
rm funds/migrations/00*.py

# 重新运行迁移
python manage.py makemigrations
python manage.py migrate
```

### 问题11: 虚拟环境激活失败(Windows)

**症状**: 运行 `venv\Scripts\activate.bat` 报错

**解决**:

1. 检查PowerShell执行策略:

```powershell
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
```

2. 或者在PowerShell中激活:

```powershell
venv\Scripts\Activate.ps1
```

### 问题12: 端口被占用

**症状**: 启动服务时报错 `Address already in use`

**解决**:

```cmd
# 方法1: 使用其他端口
python manage.py runserver 8001

# 方法2: 查找并结束占用端口的进程
# Windows
netstat -ano | findstr :8000
taskkill /PID <进程ID> /F

# Linux/Mac
lsof -ti:8000 | xargs kill -9
```

## 验证安装

安装完成后,运行以下命令验证:

```cmd
# 验证Django
python -c "import django; print('Django:', django.get_version())"

# 验证requests
python -c "import requests; print('Requests: OK')"

# 验证BeautifulSoup
python -c "import bs4; print('BeautifulSoup: OK')"

# 验证APScheduler
python -c "import apscheduler; print('APScheduler: OK')"

# 验证Plotly
python -c "import plotly; print('Plotly:', plotly.__version__)"

# 验证Django项目
python manage.py check
```

所有命令都应该输出OK,没有报错。

## 测试数据源

验证API连接是否正常:

```cmd
# 测试新浪API
python manage.py test_sina

# 测试编码
python manage.py test_encoding
```

## 下一步

安装成功后,请参考:

- [快速入门](QUICKSTART.md) - 学习如何使用系统
- [README.md](README.md) - 了解完整功能

## 卸载

如果需要卸载:

```cmd
# 1. 停止服务(Ctrl+C)

# 2. 退出虚拟环境
deactivate  # Linux/Mac
# 或直接关闭命令行窗口  # Windows

# 3. 删除虚拟环境
rmdir /s /q venv  # Windows
# 或
rm -rf venv       # Linux/Mac

# 4. 删除数据库
del db.sqlite3    # Windows
# 或
rm db.sqlite3     # Linux/Mac

# 5. 删除静态文件
rmdir /s /q staticfiles  # Windows
# 或
rm -rf staticfiles       # Linux/Mac
```

## 需要帮助?

如果遇到其他问题,请查看:

1. [README.md](README.md) - 完整文档
2. [TROUBLESHOOTING.md](TROUBLESHOOTING.md) - 故障排除指南
3. Django官方文档: https://docs.djangoproject.com/
