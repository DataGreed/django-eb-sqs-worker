import warnings

from django.conf import settings
from django.core.exceptions import ImproperlyConfigured
from django.utils.functional import cached_property


class AppSettings:
    def __init__(self):
        self._queues = {}

    @cached_property
    def AWS_EB_DEFAULT_REGION(self):
        return self._get_setting('AWS_EB_DEFAULT_REGION')

    @cached_property
    def AWS_ACCESS_KEY_ID(self):
        return self._get_setting('AWS_ACCESS_KEY_ID')

    @cached_property
    def AWS_SECRET_ACCESS_KEY(self):
        return self._get_setting('AWS_SECRET_ACCESS_KEY')

    @cached_property
    def AWS_EB_DEFAULT_QUEUE_NAME(self):
        return self._get_setting('AWS_EB_DEFAULT_QUEUE_NAME',
                                 raise_exception=False,
                                 default='django-eb-sqs-worker')

    @cached_property
    def AWS_EB_HANDLE_SQS_TASKS(self):
        return self._get_setting('AWS_EB_HANDLE_SQS_TASKS',
                                 raise_exception=False,
                                 default=False)

    @cached_property
    def AWS_EB_RUN_TASKS_LOCALLY(self):
        return self._get_setting('AWS_EB_RUN_TASKS_LOCALLY',
                                 raise_exception=False,
                                 default=False)

    @cached_property
    def AWS_EB_ALERT_WHEN_EXECUTES_LONGER_THAN_SECONDS(self):
        return self._get_setting('AWS_EB_ALERT_WHEN_EXECUTES_LONGER_THAN_SECONDS',
                                 raise_exception=False)

    @cached_property
    def enabled_tasks(self):
        enabled_tasks = self._get_setting('AWS_EB_ENABLED_TASKS',
                                          raise_exception=False,
                                          default={})
        if not isinstance(enabled_tasks, dict):
            raise ImproperlyConfigured(f"settings.EB_SQS[AWS_EB_ENABLED_TASKS]"
                                       f" must be a dict, not {type(enabled_tasks)}")

        return enabled_tasks

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
                warnings.warn(f"Setting {name} should be migrated"
                              f" to 'settings.EB_SQS' dictionary.", DeprecationWarning)
                return getattr(settings, name)


        if raise_exception:
            raise ImproperlyConfigured(f"settings.EB_SQS[{name}] should be set.")
        else:
            return default

    def reconfigure(self):
        """
        Method for testing

        Since tests modify settings at runtime, this can be used to reset values that
        should normally only be hydrated once at application startup.
        """
        self._queues = {}
        self.__dict__ = {
            k: v for k, v in self.__dict__.items()
            if not k.startswith('AWS_')
        }
        self.__dict__.pop('enabled_tasks', None)

app_settings = AppSettings()
