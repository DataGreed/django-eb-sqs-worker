import json
import logging
import time
import uuid

from django.conf import settings
from django.core.mail import mail_admins
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

        print(f"[{call_id}] Received {task.get_pretty_info_string()}. Headers: {request.headers if hasattr(request, 'headers') else request.META}")

        start_time = time.time()

        # run the task
        result = task.run_task()

        execution_time = time.time()-start_time

        print(f"{call_id} Finished {task.get_pretty_info_string()}. "
              f"Result: {result}. Execution time: {execution_time}s.")

        alert_threshold_seconds = getattr(settings, "AWS_EB_ALERT_WHEN_EXECUTES_LONGER_THAN_SECONDS", None)
        if alert_threshold_seconds:
            if execution_time > alert_threshold_seconds:
                try:
                    print(f"{call_id} took to long too finish. Reporting to admins via email. ")
                    mail_admins(f"Task {task.task_name} was running for too long",
                            f"\nTask {task.get_pretty_info_string()} (call id {call_id}) finished in {execution_time}s "
                            f"and you have "
                            f"alert thresholds set to {alert_threshold_seconds}. \nPlease check if there is "
                            f"something wrong with the task execution."
                            f"\nTask result: {result}",
                            fail_silently=False, connection=None, html_message=None)
                except Exception as e:

                    logging.error(f"Failed to send email about long-running task {call_id}: {e}", exc_info=True)

        return JsonResponse(
            {},
            status=200
        )
