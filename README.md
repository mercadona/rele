# Repository Coverage

[Full report](https://htmlpreview.github.io/?https://github.com/mercadona/rele/blob/python-coverage-comment-action-data/htmlcov/index.html)

| Name                                          |    Stmts |     Miss |   Cover |   Missing |
|---------------------------------------------- | -------: | -------: | ------: | --------: |
| rele/\_\_main\_\_.py                          |       40 |        0 |    100% |           |
| rele/apps.py                                  |        7 |        1 |     86% |        11 |
| rele/client.py                                |      116 |        3 |     97% |34-35, 129 |
| rele/config.py                                |       93 |        1 |     99% |        93 |
| rele/contrib/django\_db\_middleware.py        |       10 |        0 |    100% |           |
| rele/contrib/flask\_middleware.py             |       10 |        0 |    100% |           |
| rele/contrib/logging\_middleware.py           |       32 |        0 |    100% |           |
| rele/contrib/unrecoverable\_middleware.py     |        8 |        0 |    100% |           |
| rele/contrib/verbose\_logging\_middleware.py  |       31 |        0 |    100% |           |
| rele/discover.py                              |       31 |        0 |    100% |           |
| rele/management/commands/runrele.py           |       17 |        0 |    100% |           |
| rele/management/commands/showsubscriptions.py |       13 |        0 |    100% |           |
| rele/management/discover.py                   |       31 |        0 |    100% |           |
| rele/middleware.py                            |       40 |        0 |    100% |           |
| rele/publishing.py                            |       16 |        0 |    100% |           |
| rele/retry\_policy.py                         |       14 |        1 |     93% |        31 |
| rele/subscription.py                          |       88 |        0 |    100% |           |
| rele/worker.py                                |      115 |        1 |     99% |       241 |
| **TOTAL**                                     |  **712** |    **7** | **99%** |           |


## Setup coverage badge

Below are examples of the badges you can use in your main branch `README` file.

### Direct image

[![Coverage badge](https://raw.githubusercontent.com/mercadona/rele/python-coverage-comment-action-data/badge.svg)](https://htmlpreview.github.io/?https://github.com/mercadona/rele/blob/python-coverage-comment-action-data/htmlcov/index.html)

This is the one to use if your repository is private or if you don't want to customize anything.

### [Shields.io](https://shields.io) Json Endpoint

[![Coverage badge](https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/mercadona/rele/python-coverage-comment-action-data/endpoint.json)](https://htmlpreview.github.io/?https://github.com/mercadona/rele/blob/python-coverage-comment-action-data/htmlcov/index.html)

Using this one will allow you to [customize](https://shields.io/endpoint) the look of your badge.
It won't work with private repositories. It won't be refreshed more than once per five minutes.

### [Shields.io](https://shields.io) Dynamic Badge

[![Coverage badge](https://img.shields.io/badge/dynamic/json?color=brightgreen&label=coverage&query=%24.message&url=https%3A%2F%2Fraw.githubusercontent.com%2Fmercadona%2Frele%2Fpython-coverage-comment-action-data%2Fendpoint.json)](https://htmlpreview.github.io/?https://github.com/mercadona/rele/blob/python-coverage-comment-action-data/htmlcov/index.html)

This one will always be the same color. It won't work for private repos. I'm not even sure why we included it.

## What is that?

This branch is part of the
[python-coverage-comment-action](https://github.com/marketplace/actions/python-coverage-comment)
GitHub Action. All the files in this branch are automatically generated and may be
overwritten at any moment.