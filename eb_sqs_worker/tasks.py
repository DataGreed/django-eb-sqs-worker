from eb_sqs_worker.decorators import task


def test_task(**kwargs):
    """
    Test task, echos back all arguments that it receives.
    """

    print(f"The test task is being run with kwargs {kwargs} and will echo them back")

    return kwargs

@task
def decorated_test_task(**kwargs):
    """
    Test task, echos back all arguments that it receives.
    This one is registered using a decorator
    """

    print(f"The decorated test task is being run with kwargs {kwargs} and will echo them back")

    return kwargs

@task(queue_name="important")
def decorated_test_task_with_decorator_args(**kwargs):
    """
    Test task, echos back all arguments that it receives.
    This one is registered using a decorator
    """

    print(f"The decorated (with args) test task is being run with kwargs {kwargs} and will echo them back")

    return kwargs
