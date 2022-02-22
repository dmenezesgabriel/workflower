# Job

A task that can be execute python code, jupyter notebook or some other thing needed.

## Operator

Operator definition, define which **Operator** to use.

- alteryx
- papermill
- module
- python

### Alteryx

Alteryx job use definition tell the job to use `workflower.operators.alteryx.AlteryxOperator`, which once called will run an Alteryx `.xymd` file on command line, if the machine has a valid Alteryx installation and active license.

The Alteryx workflow `path` must be present on job's yaml definition.

```yaml
# alteryx_interval_trigger.yml
# workflow definition's version, for application control only.
version: "1.0"
workflow:
  # Workflow name must match with file name.
  name: alteryx_interval_trigger
  # Workflow jobs definition.
  jobs:
    # The name of a job does not affect the applications behaviour.
    - name: "combine_two_sheets"
      # define
      operator: alteryx
      # Alteryx .xymd file path.
      path: "C:\\Users\\gabri\\Documents\\repos\\workflower\\samples\\alteryx\\sample_combine_two_sheets.yxmd"
      # Job trigger configuration
      trigger: interval
      minutes: 1
```

### Papermill

[Papermill](https://github.com/nteract/papermill) is a python library to run [Jupyter](https://jupyter.org/) notebooks **programmatically**.

The operator used by the application is `workflower.operators.papermill.PapermillOperator`.

Papermill expects a `.ipynb` file's path as input so it can execute programmatically, and after it's execution, an `.ipynb` executed file is generated with it's cell's outputs and erros if there were any. The _output_ path is also expected, and must be in an existing directory.

At every execution a python virtual environment [(venv)](https://docs.python.org/3/library/venv.html) is created, so the packages needed for the job won't conflict with applications's packages, after the execution the environment is deleted.

You can install the packages with `%pip` cell magic:

```py
%pip install pandas

import pandas
# Will print the execution environment path.
pandas.__path__
```

```yaml
# papermill_cron_trigger.yml
# workflow definition's version, for application control only.
version: "1.0"
workflow:
  # Workflow name must match with file name.
  name: papermill_cron_trigger
  # Workflow jobs definition.
  jobs:
    # The name of a job does not affect the applications behaviour.
    - name: "notebook_install_packages"
      operator: papermill
      # Papermill paths
      # Papermill expects an .ipynb file path as input.
      input_path: "C:\\Users\\gabri\\Documents\\repos\\workflower\\samples\\notebooks\\notebook_install_packages.ipynb"
      # Papermill's execution results in a jupyter notebook output at a given path.
      output_path: "C:\\Users\\gabri\\Documents\\repos\\workflower\\samples\\notebooks\\notebook_install_packages_output.ipynb"
      # Job trigger configuration
      trigger: cron
      minute: "*/2"
```

### Python

The python job use can run a script or a code string, the execution happens on a temporary virtual environment [(venv)](https://docs.python.org/3/library/venv.html) that is deleted at the end of execution.

The operator used by the application is `workflower.operators.python.PythonOperator`, and it expects a `code` string definition or `script path`, both can use a _requirements.txt_ file for external libraries.

A script execution expects a `.py` existing file.

- **code**:

```yaml
# python_code_interval_trigger.yml
# workflow definition's version, for application control only.
version: "1.0"
workflow:
  # Workflow name must match with file name.
  name: python_code_interval_trigger
  # Workflow jobs definition.
  jobs:
    # The name of a job does not affect the applications behaviour.
    - name: "hello_python_code"
      operator: python
      # Code string
      code: "print('Hello, World!')"
      # Job trigger configuration
      trigger: interval
      minutes: 2
```

- **script**:

```yaml
# python_script_interval_trigger.yml
# workflow definition's version, for application control only.
version: "1.0"
workflow:
  # Workflow name must match with file name.
  name: python_script_interval_trigger
  jobs:
    # The name of a job does not affect the applications behaviour.
    - name: "hello_python_script"
      operator: python
      # Script path
      script_path: "C:\\Users\\gabri\\Documents\\repos\\workflower\\samples\\python\\hello_script\\hello.py"
      # Requirements path
      requirements_path: "C:\\Users\\gabri\\Documents\\repos\\workflower\\samples\\python\\hello_script\\requirements.txt"
      # Job trigger configuration
      trigger: interval
      minutes: 1
```

```yaml
# requirements.txt
requests
```

### Module

Module is a `workflower.modules.module.BaseModule` subclass which will execute what is defined on run function. This class will be used by `workflower.operators.module.ModuleOperator`.

The module operator expects a valid module path, containing a file with a `Module` class and a `run` function.

**Module example**:

```py
from workflower.modules.module import BaseModule

from playwright.sync_api import sync_playwright


class Module(BaseModule):
    def __init__(self, plugins=None) -> None:
        self._plugins = plugins

    # Expected run function with the business logic that will be called by the ModuleOperator.
    def run(self, *args, **kwargs):
        with sync_playwright() as p:
            browser = p.chromium.launch()
            page = browser.new_page()
            page.goto("http://playwright.dev")
            print(50 * "=")
            print(page.title())
            print(50 * "=")
            browser.close()
```

A Module can use application plugins.

```yaml
# module_interval_trigger.yml
# workflow definition's version, for application control only.
version: "1.0"
workflow:
  # Workflow name must match with file name.
  name: module_interval_trigger
  jobs:
    # The name of a job does not affect the applications behaviour.
    - name: "tableau_linter_module"
      operator: module
      module_path: "C:\\Users\\gabri\\Documents\\repos\\workflower\\samples\\modules\\tableau_linter\\tableau_linter.py"
      module_name: "tableau_linter"
      # Module plugins.
      plugins:
        - tableau_document_plugin
      # Job trigger configuration
      trigger: interval
      minutes: 1
```

## Triggers

- date
- interval
- cron
- dependency

### Date

```yaml
trigger: date
run_date: "2022-01-01 16:30:05"
timezone: "America/Sao_Paulo"
```

- **run_date (str)**: the date/time to run the job at, if not present will run on next execution cycle.
- **timezone (str)**: time zone for `run_date`

[APScheduler reference](https://apscheduler.readthedocs.io/en/3.x/modules/triggers/date.html)

### Interval

```yaml
trigger: interval
```

- **weeks (int)**: number of weeks to wait
- **days (int)**: number of days to wait
- **hours (int)**: number of hours to wait
- **minutes (int)**: number of minutes to wait
- **seconds (int)**: number of seconds to wait
- **start_date (str)**: starting point for the interval calculation
- **end_date (str)**: latest possible date/time to trigger on
- **timezone (str)**: time zone to use for the date/time calculations
- **jitter (int)**: delay the job execution by jitter seconds at most

[APScheduler reference](https://apscheduler.readthedocs.io/en/3.x/modules/triggers/interval.html)

### Cron

```yaml
trigger: cron
```

- **year (int|str)**: 4-digit year
- **month (int|str)**: month (1-12)
- **day (int|str)**: day of month (1-31)
- **week (int|str)**: ISO week (1-53)
- **day_of_week (int|str)**: number or name of weekday (0-6 or mon,tue,wed,thu,fri,sat,sun)
- **hour (int|str)**: hour (0-23)
- **minute (int|str)**: minute (0-59)
- **second (int|str)**: second (0-59)
- **start_date (str)**: earliest possible date/time to trigger on (inclusive)
- **end_date (str)**: latest possible date/time to trigger on (inclusive)
- **timezone (str)**: time zone to use for the date/time calculations (defaults to scheduler timezone)
- **jitter (int)**: delay the job execution by jitter seconds at most

[APScheduler reference](https://apscheduler.readthedocs.io/en/3.x/modules/triggers/cron.html)

### Dependency

```yaml
trigger: dependency
depends_on: other_job_name
```

**Example**:

```yaml
# version: is referent to yaml schema, the version of the way th yml or yaml
# file should be written, it must be string type.
version: "1.0" # str
workflow:
  # workflow's name must always match it's file name, if not will no be load,
  # in this case the file name should be dependency_log_pattern_match.yml
  # An easy way of deactivating an workflow is putting an underscore prefix in
  # it's name, like _dependency_log_pattern_match.yml
  name: dependency_log_pattern_match # str
  # Workflow can have one or more jobs
  jobs:
    # The job name does not affect in execution like workflow's, but it should
    # be clear for people you may share.
    - name: "first_job" # str
      # Job can use
      # - python
      # - papermill
      # - module
      # - alteryx
      operator: python # str
      # when job operator python, can have a code or script_path option
      code: "print('First Job!')" # str
      # trigger can be
      # - date
      # - interval
      # - cron
      # - dependency
      trigger: date # str
      # if trigger is type date and has no other key reference like :run_date:
      # it will be executed immediately accordingly to configured scheduler
      # sleep cycle
    - name: "second_job" # str
      # Job can use
      # - python
      # - papermill
      # - module
      # - alteryx
      operator: python # str
      # when job operator python, can have a code or script_path option
      code: "print('Second Job!')" # str
      # trigger can be
      # - date
      # - interval
      # - cron
      # - dependency
      trigger: dependency # str
      # If trigger is dependency it must depends on a job in the same workflow
      depends_on: first_job # str
      # The part below is optional for this trigger, you can pass a string
      # pattern to check if it's in previous job logs output.
      dependency_logs_pattern: "First" # str
      # Decide if run when has dependency log pattern and it matches with
      # previous job logs output.
      run_if_pattern_match: False # bool
```
