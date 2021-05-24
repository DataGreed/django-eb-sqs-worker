import warnings

from django.conf import settings
from django.core.exceptions import ImproperlyConfigured


class AppSettings:
    def __init__(self):
        self._enabled_tasks = {}
        self._queues = {}

    @property
    def AWS_EB_DEFAULT_REGION(self):
        return self._get_setting('AWS_EB_DEFAULT_REGION')

    @property
    def AWS_ACCESS_KEY_ID(self):
        return self._get_setting('AWS_ACCESS_KEY_ID')

    @property
    def AWS_SECRET_ACCESS_KEY(self):
        return self._get_setting('AWS_SECRET_ACCESS_KEY')

    @property
    def AWS_EB_DEFAULT_QUEUE_NAME(self):
        return self._get_setting('AWS_EB_DEFAULT_QUEUE_NAME', raise_exception=False, default='django-eb-sqs-worker')

    @property
    def AWS_EB_HANDLE_SQS_TASKS(self):
        return self._get_setting('AWS_EB_HANDLE_SQS_TASKS', raise_exception=False, default=False)

    @property
    def AWS_EB_RUN_TASKS_LOCALLY(self):
        return self._get_setting('AWS_EB_RUN_TASKS_LOCALLY', raise_exception=False, default=False)

    @property
    def AWS_EB_ALERT_WHEN_EXECUTES_LONGER_THAN_SECONDS(self):
        return self._get_setting('AWS_EB_ALERT_WHEN_EXECUTES_LONGER_THAN_SECONDS', raise_exception=False)

    @property
    def enabled_tasks(self):
        self._enabled_tasks = self._get_setting('AWS_EB_ENABLED_TASKS', raise_exception=False, default={})
        if not isinstance(self._enabled_tasks, dict):
            raise ImproperlyConfigured(f"settings.EB_SQS[AWS_EB_ENABLED_TASKS] must be a dict, "
                                       f"not {type(self._enabled_tasks)}")

        return self._enabled_tasks

    def get_queue_by_name(self, queue_name):
        if queue_name not in self._queues:
            from .sqs import sqs  # Avoid circular import
            self._queues[queue_name] = sqs.get_queue_by_name(QueueName=queue_name)

        return self._queues[queue_name]

    @staticmethod
    def _get_setting(name, raise_exception=True, default=None):
        # We cannot cache this on the instance, because Django's override_settings used
        # in test will no longer work.
        try:
            return getattr(settings, 'EB_SQS', {})[name]
        except KeyError:
            if hasattr(settings, name):
                warnings.warn(f"Setting {name} should be migrated to 'settings.EB_SQS' dictionary.", DeprecationWarning)
                return getattr(settings, name)


        if raise_exception:
            raise ImproperlyConfigured(f"settings.EB_SQS[{name}] should be set.")
        else:
            return default

app_settings = AppSettings()
