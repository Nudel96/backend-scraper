from __future__ import annotations

import redis
from rq import Queue

from .settings import settings

redis_conn = redis.Redis.from_url(settings.redis_url)
queue = Queue(connection=redis_conn)
