# helper decorators

from functools import wraps

from django.conf import settings
from django.core.exceptions import ImproperlyConfigured

from eb_sqs_worker import sqs



def task(function=None, run_locally=None, queue_name=None, task_name=None):
    """
    Decorate functions with this decorator to automatically register them in AWS_EB_ENABLED_TASKS.
    Don't supply positional arguments, use only keyword arguments, otherwise the decorator will work.
    Can be used without arguments.

    :param run_locally:
    :param queue_name:
    :param task_name:
    :return:
    """

    def actual_decorator(f):

        task_name_to_use = f"{f.__module__}.{f.__name__}"

        if task_name:
            task_name_to_use = task_name

        # sqs view will automatically check for .execute method
        task_function_execution_path = f"{f.__module__}.{f.__name__}"

        print(f"eb-sqs-worker: registering task {f} with decorator under name {task_name_to_use}; "
              f"Overrides: run_locally: {run_locally}, queue_name: {queue_name}, task_name: {task_name}")

        if hasattr(settings, "AWS_EB_ENABLED_TASKS"):
            if settings.AWS_EB_ENABLED_TASKS.get(task_name_to_use):
                raise ImproperlyConfigured(f"eb-sqs-worker error while trying to register task {task_name_to_use} through "
                                           f"decorator: task with the same name is already registered in "
                                           f"settings.AWS_EB_ENABLED_TASKS with "
                                           f"value {settings.AWS_EB_ENABLED_TASKS.get(task_name_to_use)}. "
                                           f"Consider specifying task_name in @task decorator and check that "
                                           f"your code does not reload modules with decorator functions which "
                                           f"may force them to register multiple times.")
        else:
            settings.AWS_EB_ENABLED_TASKS = {}

        # register task in settings
        settings.AWS_EB_ENABLED_TASKS[task_name_to_use] = task_function_execution_path

        # prepare the returned function

        # the function is swapped with sqs.send_task task call
        # we do this instead of adding traditional delay function,
        # so that the IDEs autocompletion for kwargs will work everywhere
        task_function = lambda **kwargs: sqs.send_task(task_name=task_name_to_use, task_kwargs=kwargs,
                                                       run_locally=run_locally, queue_name=queue_name)

        # add sync() method to this function, so the function can be called directly
        # this is needed for two reasons:
        # 1. So the worker can actually run the function instead of entering an infinite loop of re-scheduling it
        # 2. So it can be run syncronously by developer somewhere in the code if needed.
        f.execute = lambda **kwargs: f(**kwargs)


        @wraps(f)
        def wrapper(**kwargs):  # task functions cannot have *args, only **kwargs
            # **kwargs here are the kwargs of the decorated function
            return task_function(**kwargs)

        return wrapper
    if function:
        return actual_decorator(function)
    return actual_decorator