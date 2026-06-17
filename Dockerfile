# 使用 Python 3.11 作为基础镜像
FROM python:3.11-slim

# 设置工作目录
WORKDIR /app

# 安装系统依赖
RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    sqlite3 \
    vim \
    curl \
    && rm -rf /var/lib/apt/lists/*

# 复制依赖文件
COPY requirements.txt .

# 安装 Python 依赖
RUN pip install --no-cache-dir -r requirements.txt

# 复制项目文件
COPY . .

# 转换 shell 脚本的换行符（Windows CRLF -> Linux LF）
RUN sed -i 's/\r$//' docker-start.sh start.sh

# 创建必要的目录
RUN mkdir -p logs db static media

# 设置环境变量
ENV PYTHONUNBUFFERED=1
ENV DJANGO_SETTINGS_MODULE=jijinweb.settings

# 暴露端口
EXPOSE 8000

# 使用启动脚本
CMD ["bash", "docker-start.sh"]
