# Workflower

Make your workday smell like daisies.

From developers to data people (engineers, analysts and scientists).

[docs](https://dmenezesgabriel.github.io/workflower/)

## Short Description

A minimal workflow orchestrator for data pipelines, made to work on a windows or linux machine.

## Architecture

- Built on top of [APScheduler](https://github.com/agronholm/apscheduler)

## Usage

Configure a .env file following the _.env.\*.template_ examples then:

```sh
./run.sh
```

or:

```sh
alias "workflower"="./run.sh"
workflower
```

## Workflow samples

### Dependencies

**With expected pattern in text**:

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
      uses: python # str
      # when job uses python, can have a code or script_path option
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
      uses: python # str
      # when job uses python, can have a code or script_path option
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

## Glossary

- **Workflow**:
  A set of jobs that should be executed with some recurrence.
- **Job**:
  A task that can be execute a python code, a jupyter notebook or some other thing needed.
- **Uses**:
  What is the operator where the job is executed on, like python, papermill(runs jupyter notebooks).
- **Trigger**:
  Type of schedule definition, can be a fixed date, cron, or time interval.
- **Plugins**:
  Plugins are operator's extensions that helps to execute a job, that can be a pack with a bunch of code classes to help publish a dashboard from an external source.
- **Plugin Components**:
  Components are plugin parts, or code classes with auxiliary functions.
