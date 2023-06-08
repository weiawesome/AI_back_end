FROM debian

# 安装必要的软件
RUN apt-get update && apt-get install -y \
    default-mysql-client \
    redis-tools \
    cron \
    && rm -rf /var/lib/apt/lists/*


COPY redis_backup.sh /redis_backup.sh
RUN chmod +x /redis_backup.sh

COPY my_crontab /my_crontab
RUN crontab /my_crontab

# 运行 cron 服务
CMD ["cron", "-f"]
