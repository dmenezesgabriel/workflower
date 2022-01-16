# Job

A **job** is a workflow's task that should be scheduled.

A job can be:

- [x] An Alteryx workflow
- [x] An jupyter notebook
- [ ] A Knime workflow
- [ ] A Python script
- [ ] An utility function

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

### Date

### Interval

### Cron
