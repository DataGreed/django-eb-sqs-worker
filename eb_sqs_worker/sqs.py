import json
import uuid

import boto3
from django.conf import settings
from django.core.exceptions import ImproperlyConfigured
from django.utils.module_loading import import_string
import logging


logger = logging.getLogger(__name__)
try:
    AWS_REGION = settings.AWS_EB_DEFAULT_REGION
except AttributeError:
    raise ImproperlyConfigured("settings.AWS_EB_DEFAULT_REGION not set, please set it to use eb_sqs_worker django app")

# TODO: make it lazy so we can run tests without setting this settings?
sqs = boto3.resource('sqs',
                     region_name=AWS_REGION,
                     aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
                     aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY)


def send_task(task_name, task_kwargs, run_locally=None, queue_name=None):
    """
    Sends task to SQS queue to be run asynchronously on worker environment instances.
    If settings.AWS_EB_RUN_TASKS_LOCALLY  is set to True, does not send the task
    to SQS, but instead runs it right away in synchronous mode. May be useful
    for testing when no SQS worker is set up.

    :param task_name name of the task to run.
    :param task_kwargs kwargs that are passed to the task
    :param run_locally if set, forces the task to be run locally or sent to SQS
    regardless of what settings.AWS_EB_RUN_TASKS_LOCALLY is set to.
    :return:
    """

    task_data = {
        'task': task_name,
        'arguments': task_kwargs
    }

    if run_locally is None:
        run_locally = getattr(settings, "AWS_EB_RUN_TASKS_LOCALLY", False)

    if run_locally:

        task_id = uuid.uuid4().hex

        task = SQSTask(task_data)
        print(f"[{task_id}] Running task locally in sync mode: {task.get_pretty_info_string()}")

        result = task.run_task()
        print(f"[{task_id}] Task result: {result}")

    else:

        if queue_name is None:
            try:
                queue_name = settings.AWS_EB_DEFAULT_QUEUE_NAME
            except AttributeError:
                raise ImproperlyConfigured("settings.AWS_EB_DEFAULT_QUEUE_NAME must be set to send task to SQS queue")

            # TODO: cache queues instead of looking the up every time
        try:
            # Get the queue. This returns an SQS.Queue instance
            queue = sqs.get_queue_by_name(QueueName=queue_name)
        except:
            queue = sqs.create_queue(QueueName=queue_name)


        # send task to sqs workers
        # see https://boto3.amazonaws.com/v1/documentation/api/latest/guide/sqs.html
        response = queue.send_message(MessageBody=json.dumps(task_data))
        logger.info(f"Sent message {task_data} to SQS queue {queue_name}. Got response: {response}")

        # print(response.get('MessageId'))
        # print(response.get('MD5OfMessageBody'))


class SQSTask:

    def __init__(self, data, request=None):
        """
        :param data: dictionary with parsed request data that is used to populate
        task fields.
        Expects the following dict format:

        {
            "task": "job_name", # task name in settings.AWS_EB_ENABLED_TASKS
            "arguments": {  # arguments passed as kwargs to task function
                "someArgument": "someValue",
                "otherArgument": 123,
                "anotherArgument": [1,"a", 3,4]
            }
        }
        """

        self.data = data
        self.task_name = data.get('task')
        self.task_kwargs = data.get('arguments', {})    # task may have no args
        self.last_result = None
        self.scheduled_time = None
        self.sender_id = None

        # check that the task is specified in body if it's not, try to get it from header as it can be a peridoic job
        #  see more here https://docs.aws.amazon.com/elasticbeanstalk/latest/dg/using-features-managing-env-tiers
        # .html#worker-periodictasks
        if not self.task_name and request is not None:
            debug_meta = request.META
            debug_headers = request.headers
            self.task_name = request.headers.get('X-Aws-Sqsd-Taskname')
            self.scheduled_time = request.headers.get('X-Aws-Sqsd-Scheduled-At')
            self.sender_id = request.headers.get('X-Aws-Sqsd-Sender-Id')

        if not self.task_name:
            raise ValueError("SQSTask must have a name either in body, or in X-Aws-Sqsd-Taskname header")

    def is_periodic(self):
        """
        :return: True if the task was set using amazon's periodic scheduler See
        https://docs.aws.amazon.com/elasticbeanstalk/latest/dg/using-features-managing-env-tiers.html#worker
        -periodictasks
        """
        return self.scheduled_time is not None

    def run_task(self):
        """
        Looks up the function associated with task_name in
        settings.AWS_EB_ENABLED_TASKS keys and calls corresponding function
        with passed keyword arguments. Be sure that your task functions
        all have keyword arguments.

        AWS_EB_ENABLED_TASKS must be a dictionary:
        {
            "task_name": "path.to.task.function"
        }
        :return:
        """
        if not getattr(settings, "AWS_EB_ENABLED_TASKS", None):
            raise ImproperlyConfigured(f"settings.AWS_EB_ENABLED_TASKS not set, cannot run task {self.task_name}")

        if not isinstance(settings.AWS_EB_ENABLED_TASKS, dict):
            raise ImproperlyConfigured(f"settings.AWS_EB_ENABLED_TASKS must be a dict, "
                                       f"not {type(settings.AWS_EB_ENABLED_TASKS)}")

        try:
            task_method_path = settings.AWS_EB_ENABLED_TASKS[self.task_name]
        except KeyError:
            raise ImproperlyConfigured(f"Task named {self.task_name} is not defined in settings.AWS_EB_ENABLED_TASKS")

        task_method = import_string(task_method_path)

        # check for method added by @task decorator. If present, use it instead
        if hasattr(task_method, "execute"):
            if callable(task_method.execute):
                task_method = task_method.execute

        if not callable(task_method):
            raise ImproperlyConfigured(f"Tasks defined in AWS_EB_ENABLED_TASKS must be callables. "
                                       f"Object for task f{self.task_name} is not callable, "
                                       f"it's a {type(task_method)}'")

        result = task_method(**self.task_kwargs)
        self.last_result = result

        # TODO: make sure that the returned result is serialized and can be displayed in json correctly

        return result

    def get_pretty_info_string(self):
        periodic_marker = ""
        periodic_info = ""
        if self.is_periodic():
            periodic_marker = "Periodic "
            periodic_info = f", scheduled at {self.scheduled_time} by {self.sender_id}"

        result = f"{periodic_marker}Task({self.task_name}, kwargs: {self.task_kwargs}{periodic_info})"

        return result
