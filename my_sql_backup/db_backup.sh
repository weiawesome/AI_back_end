#!/bin/sh
set -e
# 指定將存放備份檔案的目錄
BACKUP_DIR=/backup

# 建立備份檔案的名稱
BACKUP_NAME=mysql_backup_`date +%Y_%m_%d_%H_%M_%S`.sql
# 實際的備份命令
mysqldump -h $MYSQL_HOST -u $MYSQL_USER --password=$MYSQL_PASSWORD $MYSQL_DATABASE > $BACKUP_DIR/$BACKUP_NAME
