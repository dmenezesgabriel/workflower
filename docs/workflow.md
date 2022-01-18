# Workflow

Workflow is defined on a `.yml` file and can contain multiple jobs.

- Workflow name must be unique
- Workflow file name must be the same of workflow name

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
