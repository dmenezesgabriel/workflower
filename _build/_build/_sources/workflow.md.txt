# Workflow

Workflow is defined on a `.yml` file and can contain multiple jobs.

- Workflow name must be unique
- Workflow file name must be the same of workflow name, if not won't load
- If a workflow file has been modified, modifications will be applied on next cycle
- If a workflow file has been removed, the scheduled for all it's jobs will be removed
- Dependency trigger jobs must be defined after it's depends_on job

  Example:

```yml
version: "1.0"
# This a Workflow definition
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

## Tips

An easy way of deactivating an workflow is inserting a underscore `_` at the beginning of it's file name, so it won't match with defined workflow name inside yaml or yml file.

## Functioning

```py
# --------------------------------------------------------------------------- #
# Workflow
# --------------------------------------------------------------------------- #
workflow.file_exists # ?
workflow.is_active # ?
workflow.modified_since_last_load # ?

if workflow.file_exists is True:
  workflow.is_active = True
  workflow.update_jobs
  workflow.schedule_jobs

if workflow.file_exists is False:
  # Remove
  workflow.is_active = False
  workflow_unschedule_jobs
  workflow.update_jobs
# --------------------------------------------------------------------------- #
if (
    workflow.file_exists is True and
    workflow.modified_since_last_load is False
  ):
  workflow.is_active = True
  workflow.schedule_jobs


if (
    workflow.file_exists is True and
    workflow.modified_since_last_load is True
  ):
  workflow.is_active = True
  # Reschedule
  workflow.unschedule_jobs
  workflow.update_jobs
  workflow.schedule_jobs
# --------------------------------------------------------------------------- #
# Jobs
# --------------------------------------------------------------------------- #
workflow.file_exists # ?
workflow.is_active # ?
workflow.modified_since_last_load # ?

job.exists # ?
job.is_active #?
job.modified # ?
```
