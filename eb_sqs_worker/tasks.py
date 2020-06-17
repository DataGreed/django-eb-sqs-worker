def test_task(**kwargs):
    """
    Test task, echos back all arguments that it receives.
    """

    print(f"The test task is being run with kwargs {kwargs} and will echo them back")

    return kwargs
