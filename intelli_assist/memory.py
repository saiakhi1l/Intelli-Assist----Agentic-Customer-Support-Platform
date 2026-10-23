import json
from collections import defaultdict

class SessionMemory:
    def __init__(self, settings):
        self.settings = settings
        self.local = defaultdict(list)
        self.redis = None
        if settings.redis_enabled:
            from redis import Redis
            self.redis = Redis.from_url(settings.redis_url, decode_responses=True, socket_timeout=2)

    def get(self, session_id):
        if self.redis:
            raw = self.redis.get(f"intelli:session:{session_id}")
            return json.loads(raw) if raw else []
        return list(self.local[session_id])

    def append(self, session_id, user, assistant):
        history = self.get(session_id)
        history.extend([{"role":"user","content":user},{"role":"assistant","content":assistant}])
        history = history[-self.settings.max_history_turns * 2:]
        if self.redis:
            self.redis.setex(f"intelli:session:{session_id}", self.settings.redis_ttl_seconds, json.dumps(history))
        else:
            self.local[session_id] = history
