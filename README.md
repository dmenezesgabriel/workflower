# Workflower

[![dmenezesgabriel](https://circleci.com/gh/dmenezesgabriel/workflower.svg?style=shield)](LINK)

Make your workday smell like daisies.

From developers to data people (engineers, analysts and scientists).

- [docs](https://dmenezesgabriel.github.io/workflower/)
- [repository](https://github.com/dmenezesgabriel/workflower)

## Short Description

A minimal workflow orchestrator for data pipelines, made to work on a windows or linux machine.

## Architecture

- Built on top of [APScheduler](https://github.com/agronholm/apscheduler)

## Usage

1. Configure a .env file following the _.env.\*.template_ examples then:

```sh
# .env
# Application cycle time between workflow files loading.
export CYCLE=20
# Schedule time zone
export TIME_ZONE="America/Sao_Paulo"
# =========================================================================== #
# Workflows configuration
# =========================================================================== #
# Path from where workflow files should be loaded
export WORKFLOWS_FILES_PATH="./samples/workflows"
# =========================================================================== #
# Database configuration
# =========================================================================== #
# Database URL
export APP_DATABASE_URL="sqlite:///data/app-dev.sqlite"
# =========================================================================== #
# Logging configuration
# =========================================================================== #
# Logging level of detail
# - DEBUG
# - ERROR
export LOG_LEVEL="DEBUG"
# Logging file name
export LOGGING_FILE="log.log"
# Logging File path
export LOGGING_PATH="./data/log/"
# Logging files max bytes
export LOGGING_FILE_MAX_BYTES=90000
# Logging files backup count
export LOGGING_FILE_BACKUP_COUNT=1
# =========================================================================== #
# Virtual environments configuration
# =========================================================================== #
# Virtual environments Path
export ENVIRONMENTS_DIR="./data/environments"
#  Jupyter Kernels path
export KERNELS_SPECS_DIR="./data/kernel_specs"
# =========================================================================== #
# Plugins configuration
# =========================================================================== #
# Tableau server plugin
# Tableau server url
export TABLEAU_SERVER_URL="your_server_url"
# Tableau server user's generated token name
export TABLEAU_TOKEN_NAME="your_token_name"
# Tableau server user's generated token value
export TABLEAU_TOKEN_VALUE="yout_token_Value"
# Tableau server name also knowed as id
export TABLEAU_SITE_ID="yout_site_id"
```

2. Run the shell cli

```sh
./run.sh
```

or:

```sh
alias "workflower"="./run.sh"
workflower
```

3. Type the wanted command after cli initialization:

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
- **Operator**:
  The operator where the job is executed on, like python, papermill(runs jupyter notebooks).
- **Trigger**:
  Type of schedule definition, can be a fixed date, cron, or time interval.
- **Plugins**:
  Plugins are operator's extensions that helps to execute a job, that can be a pack with a bunch of code classes to help publish a dashboard from an external source.
- **Plugin Components**:
  Components are plugin parts, or code classes with auxiliary functions.
