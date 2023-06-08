#!/bin/sh

if [ "$REDIS_PASSWORD" ]; then
    grep -qF "requirepass ${REDIS_PASSWORD}" /usr/local/etc/redis/redis.conf || echo "requirepass ${REDIS_PASSWORD}" >> /usr/local/etc/redis/redis.conf
fi

exec redis-server /usr/local/etc/redis/redis.conf
