# Job

A **job** is a workflow's task that should be scheduled.

A job can be:

- Python script
- Jupyter notebook
- Python module
- Alteryx workflow

```yml
# This a Workflow definition
version: "1.0"
workflow:
  # Workflow name must be unique
  name: alteryx_sample_date_trigger
  # This is a Job definition
  jobs:
    - name: "sample_combine_two_sheets"
      uses: alteryx
      path: "C:\\Users\\gabri\\Documents\\repos\\workflower\\samples\\alteryx\\sample_combine_two_sheets.yxmd"
      trigger: date
      run_date: "2022-01-14 18:55:05"
```

## Uses

- alteryx
- papermill

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

- [APScheduler reference](https://apscheduler.readthedocs.io/en/3.x/modules/triggers/date.html)

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

- [APScheduler reference](https://apscheduler.readthedocs.io/en/3.x/modules/triggers/interval.html)

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

- [APScheduler reference](https://apscheduler.readthedocs.io/en/3.x/modules/triggers/cron.html)

### Dependency

```yaml
trigger: dependency
depends_on: other_job_name
```
