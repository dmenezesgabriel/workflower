# Job

A **job** is a workflow's task that should be scheduled.

## Uses

Uses definition, define which **Operator** to use.

- alteryx
- papermill
- module
- python

## alteryx

```yaml
# alteryx_interval_trigger.yml
# workflow definition's version, for application use only.
version: "1.0"
workflow:
  # Workflow name must match with file name.
  name: alteryx_interval_trigger
  # Workflow jobs definition
  jobs:
    # The name of a job does not affect the applications behaviour
    - name: "combine_two_sheets"
      # define
      uses: alteryx
      path: "C:\\Users\\gabri\\Documents\\repos\\workflower\\samples\\alteryx\\sample_combine_two_sheets.yxmd"
      trigger: interval
      minutes: 1
```

## papermill

[Papermill](https://github.com/nteract/papermill) is a python library to run [Jupyter](https://jupyter.org/) notebooks **programmatically**.

```yaml
version: "1.0"
workflow:
  name: papermill_cron_trigger
  jobs:
    - name: "notebook_install_packages"
      uses: papermill
      # Papermill paths
      input_path: "C:\\Users\\gabri\\Documents\\repos\\workflower\\samples\\notebooks\\notebook_install_packages.ipynb"
      output_path: "C:\\Users\\gabri\\Documents\\repos\\workflower\\samples\\notebooks\\notebook_install_packages_output.ipynb"
      # trigger config
      trigger: cron
      minute: "*/2"
```

## python

- **code**:

```yaml
version: "1.0"
workflow:
  name: python_code_interval_trigger
  jobs:
    - name: "hello_python_code"
      uses: python
      code: "print('Hello, World!')"
      trigger: interval
      minutes: 2
```

- **script**:

```yaml
version: "1.0"
workflow:
  name: python_script_interval_trigger
  jobs:
    - name: "hello_python_script"
      uses: python
      script_path: "C:\\Users\\gabri\\Documents\\repos\\workflower\\samples\\python\\hello_script\\hello.py"
      requirements_path: "C:\\Users\\gabri\\Documents\\repos\\workflower\\samples\\python\\hello_script\\requirements.txt"
      trigger: interval
      minutes: 1
```

## module

Module is a `workflower.operators.operator.BaseOperator` subclass which will execute what is defined on run function.

A Module can use application plugins.

```yaml
version: "1.0"
workflow:
  name: module_interval_trigger
  jobs:
    - name: "tableau_linter_module"
      uses: module
      module_path: "C:\\Users\\gabri\\Documents\\repos\\workflower\\samples\\modules\\tableau_linter\\tableau_linter.py"
      module_name: "tableau_linter"
      plugins:
        - tableau_document_plugin
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

- run_date (str): the date/time to run the job at, if not present will run on next execution cycle.
- timezone (str): time zone for `run_date`

[APScheduler reference](https://apscheduler.readthedocs.io/en/3.x/modules/triggers/date.html)

### Interval

```yaml
trigger: interval
```

- weeks (int): number of weeks to wait
- days (int): number of days to wait
- hours (int): number of hours to wait
- minutes (int): number of minutes to wait
- seconds (int): number of seconds to wait
- start_date (str): starting point for the interval calculation
- end_date (str): latest possible date/time to trigger on
- timezone (str): time zone to use for the date/time calculations
- jitter (int): delay the job execution by jitter seconds at most

[APScheduler reference](https://apscheduler.readthedocs.io/en/3.x/modules/triggers/interval.html)

### Cron

```yaml
trigger: cron
```

- year (int|str): 4-digit year
- month (int|str): month (1-12)
- day (int|str): day of month (1-31)
- week (int|str): ISO week (1-53)
- day_of_week (int|str): number or name of weekday (0-6 or mon,tue,wed,thu,fri,sat,sun)
- hour (int|str): hour (0-23)
- minute (int|str): minute (0-59)
- second (int|str): second (0-59)
- start_date (str): earliest possible date/time to trigger on (inclusive)
- end_date (str): latest possible date/time to trigger on (inclusive)
- timezone (str): time zone to use for the date/time calculations (defaults to scheduler timezone)
- jitter (int): delay the job execution by jitter seconds at most

[APScheduler reference](https://apscheduler.readthedocs.io/en/3.x/modules/triggers/cron.html)

### Dependency

```yaml
trigger: dependency
depends_on: other_job_name
```

**Example**:

```yaml
version: "1.0"
workflow:
  name: papermill_cron_trigger_with_deps
  jobs:
    - name: "notebook_install_packages"
      uses: papermill
      # Papermill paths
      input_path: "C:\\Users\\gabri\\Documents\\repos\\workflower\\samples\\notebooks\\notebook_install_packages.ipynb"
      output_path: "C:\\Users\\gabri\\Documents\\repos\\workflower\\samples\\notebooks\\notebook_install_packages_output.ipynb"
      # trigger config
      trigger: cron
      minute: "*/3"
      # Second job, triggered after first
    - name: "python_get_argv"
      uses: python
      # Papermill paths
      script_path: "C:\\Users\\gabri\\Documents\\repos\\workflower\\samples\\python\\sys_argv\\get_argv.py"
      trigger: dependency
      depends_on: notebook_install_packages
```
