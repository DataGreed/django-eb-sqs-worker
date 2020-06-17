# django-eb-sqs-worker
Django SQS Worker for Amazon Elastic Beanstalk.

Lets you handle async jobs on Elastic Beanstalk Worker Environment sent via SQS and provides methods to send tasks to worker.

You can use the same Django codebase for both your Web Tier and Worker Tier environments and send tasks 
from Web environment to Worker environment. Amazon fully manages autoscaling for you. 
Tasks are sent via Amazon Simple Queue Service and are delivered to your worker with Elastic Beanstalk's SQS daemon.

Created by Alexey "DataGreed" Strelkov, published under MIT License. See LICENCE file for details.

# Installation

Install using pip (#TODO: publish on pip)

```
pip install django-eb-sqs-worker
```

`#TODO settings`
`#TODO urls`

# Usage

`#TODO`

## Defining Jobs

`#TODO`

## Sending jobs to worker

`#TODO`

## Periodic jobs

`#TODO`

# Additional configuration

`#TODO list all settings`

# Security

`#TODO`

# Tips

`#TODO`

## Delay abstraction

`#TODO`

## Using different cron files for different environments

`#TODO`

# Testing

`#TODO`

# Contributing

`#TODO`