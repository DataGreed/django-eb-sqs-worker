import json
import time
import uuid

from django.conf import settings
from django.shortcuts import render

# Create your views here.
from django.utils.decorators import method_decorator
from django.views import View
from django.http import JsonResponse, Http404, HttpResponseBadRequest
from django.views.decorators.csrf import csrf_exempt

from eb_sqs_worker.sqs import SQSTask


@method_decorator(csrf_exempt, name='dispatch')  # otherwise will hit csrf protection
class HandleSQSTaskView(View):

    def post(self, request):
        """
        Handles incoming SQS tasks from Elastic Beanstalk SQS daemon.
        More info about it here: https://docs.aws.amazon.com/elasticbeanstalk/latest/dg/using-features-managing-env-tiers.html#worker-daemon
        :param request:
        :return:
        """
        if not getattr(settings, "AWS_EB_HANDLE_SQS_TASKS", False):
            # if this django instance is not set to handle
            # incoming SQS tasks from Elastic Beanstalk SQS Daemon,
            # then ignore them as this may pose a security risk.
            # Only worker environments that are isolated from the internet
            # can be set to handle incoming SQS messages, otherwise
            # anyone can post them.
            raise Http404()

        # save in context for easier debugging in sentry
        debug_meta = request.META
        debug_headers = request.headers

        # check user-agent just to defend ourselves from script kiddies
        if "aws-sqsd" not in request.META.get('HTTP_USER_AGENT', ''):
            return JsonResponse({},status=400)

        # generate call id so we can find all log records corresponding
        # to one task easily
        call_id = uuid.uuid4().hex

        body_json = {}
        # parse the message body to extract the task if the task is not periodic
        # if this header is set, the task is periodic and there should be no
        # body expected
        if not (request.headers.get('X-Aws-Sqsd-Taskname')):
            body_json = json.loads(request.body)

        # create task instance and try to run it
        task = SQSTask(body_json, request)

        print(f"[{call_id}] Received {task.get_pretty_info_string()}.")

        start_time = time.time()

        # run the task
        result = task.run_task()

        execution_time = time.time()-start_time

        print(f"{call_id} Finished {task.get_pretty_info_string()}. "
              f"Result: {result}. Execution time: {execution_time}s.")

        return JsonResponse(
            {},
            status=200
        )
