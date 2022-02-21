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

then:

```sh
Starting CLI...

Setting venv paths
Setting env paths on windows

################################################################
Hello gabri,
Welcome to CLI Helper, version 0.1.0
################################################################

Commands:
- help: promp command options
- setup: create /c/Users/gabri/environments/workflower
- dev: init database and run app with dev config
- prod: init database and run app with prod config
- env: init database and run app with .env config
- test: run tests
- exit: exit program

Waiting command:

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
