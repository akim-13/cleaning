from django.apps import AppConfig
import redis

class MainConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'main'

    # Flushes the Redis database of active users on server startup.
    redis_client = redis.Redis(host='localhost', port=6379, db=0)
    redis_client.flushdb()
