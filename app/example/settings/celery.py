# settings.py
from celery.schedules import crontab

from .environment import Env


# Celery settings
CELERY_BROKER_URL = f'redis://{Env.REDIS_HOST}:{Env.REDIS_PORT}/{Env.REDIS_DB}'  # Use Redis as the message broker
CELERY_RESULT_BACKEND = f"redis://{Env.REDIS_HOST}:{Env.REDIS_PORT}/{Env.REDIS_DB}"
CELERY_ACCEPT_CONTENT = ['json']
CELERY_TASK_SERIALIZER = 'json'
CELERY_RESULT_SERIALIZER = 'json'

# Timezone settings
CELERY_TIMEZONE = 'UTC'  # Or your preferred timezone
CELERY_ENABLE_UTC = True


CELERY_BEAT_SCHEDULE = {
    'create-question-every-hour': {
        'task': 'questions.tasks.create_random_question',
        'schedule': crontab(minute=0, hour='*/1'),
    },
}
