from django.apps import AppConfig
import redis

class MainConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'main'
    verbose_name = 'Панель управления'

    def ready(self):
        from django.db.utils import OperationalError, ProgrammingError
        from django.contrib.auth.models import Group
        
        try:
            roles = [
                ('manager_contractor', 'Менеджер Исполнитель'),
                ('manager_customer', 'Менеджер Заказчик'),
                ('auditor_contractor', 'Аудитор Исполнитель'),
                ('auditor_customer', 'Аудитор Заказчик'),
                ('representative', 'Представитель Клининговой Компании'),
                ('configurator', 'Конфигуратор')
            ]

            for role_name, _ in roles:
                Group.objects.get_or_create(name=role_name)

        except (OperationalError, ProgrammingError):
            # If the database isn't ready yet, we'll skip creating groups for now.
            pass

    # Flushes the Redis database of active users on server startup.
    redis_client = redis.Redis(host='localhost', port=6379, db=0)
    redis_client.flushdb()
