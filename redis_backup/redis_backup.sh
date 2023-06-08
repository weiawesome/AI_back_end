#!/bin/bash

# 指定将存放备份文件的目录
BACKUP_DIR=/backup

# 建立备份文件的名称
BACKUP_NAME=redis_backup_`date +%Y_%m_%d_%H_%M_%S`.rdb

# Redis 服务器的主机名和密码
REDIS_HOST=redis
REDIS_PASSWORD={$REDIS_PASSWORD}

# 在 Redis 容器内执行 BGSAVE 命令生成备份
docker exec -it $REDIS_HOST redis-cli -a $REDIS_PASSWORD BGSAVE

# 由于 BGSAVE 是异步的，我们需要等待一段时间确保备份已经完成
sleep 60

# 将生成的 dump.rdb 文件复制到你的备份目录，并重命名
docker exec -it $REDIS_HOST sh -c "cp /data/dump.rdb $BACKUP_DIR/$BACKUP_NAME"
