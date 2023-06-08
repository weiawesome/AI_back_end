FROM redis
RUN mkdir -p /var/lib/redis \
    && chown redis:redis /var/lib/redis \
    && chmod 700 /var/lib/redis

COPY redis.conf /usr/local/etc/redis/redis.conf
COPY start-redis.sh /start-redis.sh

RUN chown redis:redis /usr/local/etc/redis/redis.conf \
    && chmod 700 /usr/local/etc/redis/redis.conf \
    && chown redis:redis /start-redis.sh \
    && chmod +x /start-redis.sh

USER redis
CMD [ "/start-redis.sh" ]
