[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

# django-eb-sqs-worker

Django Background Tasks for Amazon Elastic Beanstalk.

Lets you handle background jobs on [Elastic Beanstalk Worker Environment](https://docs.aws.amazon.com/elasticbeanstalk/latest/dg/using-features-managing-env-tiers.html) sent via SQS and provides methods to send tasks to worker.

You can use the same Django codebase for both your Web Tier and Worker Tier environments and send tasks 
from Web environment to Worker environment. Amazon fully manages autoscaling for you. 
Tasks are sent via [Amazon Simple Queue Service](https://docs.aws.amazon.com/AWSSimpleQueueService/latest/SQSDeveloperGuide/welcome.html) and are delivered to your worker with [Elastic Beanstalk's SQS daemon](https://docs.aws.amazon.com/elasticbeanstalk/latest/dg/using-features-managing-env-tiers.html#worker-daemon).

Created by Alexey "DataGreed" Strelkov.

## Installation

Install using pip `#TODO: publish on pip`
```
pip install -e git+git//github.com/DataGreed/django-eb-sqs-worker.git#egg=django-eb-sqs-worker
```


```
pip install django-eb-sqs-worker
```

`#TODO settings`

`#TODO urls`

## Usage

`#TODO`

### Defining Jobs

`#TODO`

### Sending jobs to worker

`#TODO`

### Periodic jobs

`#TODO`

## Settings

### AWS_EB_ENABLED_TASKS
Dictionary of enabled tasks. Routes task names to actual task methods.

E.g.:

```python
AWS_EB_ENABLED_TASKS = {
    # name used in serialization   # path to actual method that does the job
    "accounts_confirmation_email": "accounts.tasks.send_confirmation_email",
    "analytics_track_event": "analytics.tasks.track_event"
}
``` 

### AWS_EB_DEFAULT_REGION

Default Elastic Beanstalk Region. Use the one that your app id deployed in. 

### AWS_EB_DEFAULT_QUEUE_NAME

Name of the queue used by default.

### AWS_ACCESS_KEY_ID

Amazon Access Key Id, refer to [the docs](https://docs.aws.amazon.com/general/latest/gr/aws-sec-cred-types.html#access-keys-and-secret-access-keys)

### AWS_SECRET_ACCESS_KEY

Amazon Secret Access Key, refer to [the docs](https://docs.aws.amazon.com/general/latest/gr/aws-sec-cred-types.html#access-keys-and-secret-access-keys)

## Security

`#TODO`

## Tips

`#TODO`

### Accessing Web Tier Database from Worker

`#TODO`

### Delay abstraction

`#TODO`

### Using different cron files for different environments

`#TODO`

## Testing

### Synchronous mode

`#TODO`

### Testing django-eb-sqs-worker itself

`#TODO`

## Contributing

`#TODO`

# TODOs

- take advantage of the new [environment link feature](https://docs.aws.amazon.com/elasticbeanstalk/latest/dg/environment-cfg-links.html)
- decorators for easier setup

---
Search tags 

Django Elastic Beanstalk Worker Web Tier Asynchronous Jobs Background Tasks SQS  