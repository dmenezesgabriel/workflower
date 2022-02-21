# Workflow

A set of **jobs**.

Workflow is defined on a `.yml` or `.yaml` file and can contain multiple jobs.

- Workflow name **must** be unique
- Workflow file name must be the **same** of workflow name, if not won't load
- If a workflow file has been modified, modifications will be applied on next cycle
- If a workflow file has been removed, the scheduled for all it's jobs will be removed
- Dependency trigger jobs must be defined after it's depends_on job

  Example:

```yaml
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

### Deactivating .yml workflows

An easy way of deactivating an workflow is inserting a underscore `_` at the beginning of it's file name, so it won't match with defined workflow name inside yaml or yml file.
