FROM debian

# 安装必要的软件
RUN apt-get update && apt-get install -y \
    default-mysql-client \
    redis-tools \
    cron \
    && rm -rf /var/lib/apt/lists/*

COPY db_backup.sh /db_backup.sh
RUN chmod +x /db_backup.sh

RUN (crontab -l 2>/dev/null; echo "0 3 * * * /db_backup.sh") | crontab -

CMD ["cron", "-f"]
