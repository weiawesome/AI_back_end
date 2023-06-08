FROM mysql:8.0.26
# 環境變數設定，這些將在 init.sql 中被用到
ENV MYSQL_ROOT_PASSWORD=${MYSQL_ROOT_PASSWORD}
ENV MYSQL_DATABASE=${DATABASE_NAME}
ENV MYSQL_USER=${DATABASE_USER}
ENV MYSQL_PASSWORD=${DATABASE_PASS}

# 將你的 init.sql 腳本加入到 Docker 映象中，Docker 會在 MySQL 服務啟動時執行這個腳本
ADD init-db.sh /docker-entrypoint-initdb.d/init-db.sh

# 給予腳本執行權限
RUN chmod +x /docker-entrypoint-initdb.d/init-db.sh