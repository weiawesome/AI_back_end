#!/bin/bash

# 指定将存放备份文件的目录
BACKUP_DIR=/backup

# 建立备份文件的名称
BACKUP_NAME=redis_backup_`date +%Y_%m_%d_%H_%M_%S`.rdb

# 使用redis-cli命令执行备份，并将备份文件保存到容器内
redis-cli -h redis SAVE
redis-cli -h redis --rdb $BACKUP_DIR/$BACKUP_NAME
