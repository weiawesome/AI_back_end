#!/bin/bash

DATABASE_NAME=$DATABASE_NAME
DATABASE_USER=$DATABASE_USER
DATABASE_PASS=$DATABASE_PASS

# 創建MySQL命令
MYSQL_CMD="mysql --user=root --password=$MYSQL_ROOT_PASSWORD"

# 創建數據庫、用戶，並授予權限
SQL_QUERY="CREATE DATABASE IF NOT EXISTS $DATABASE_NAME; CREATE USER '$DATABASE_USER'@'%' IDENTIFIED BY '$DATABASE_PASS'; GRANT ALL PRIVILEGES ON $DATABASE_NAME.* TO '$DATABASE_USER'@'%';"

# 執行命令
echo $SQL_QUERY | $MYSQL_CMD
