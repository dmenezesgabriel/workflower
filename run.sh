#!/bin/bash
# =========================================================================== #
# Clean app data
# =========================================================================== #
set -e
# set -x # DEBUG
VERSION=0.1.0
NAME="CLI Helper"

echo "==========================================================="
echo "Hello $(whoami),"
echo "Welcome to $NAME, version $VERSION"
echo "==========================================================="
echo "Commands:"
echo "- setup: create ~/environments/workflower"
echo "- dev: init database and run app with dev config"
echo "- prod: init database and run app with prod config"
echo "- env: init database and run app with .env config"
echo "- test: run tests"
echo "- exit: exit program"
echo "==========================================================="

# Check platform
unameOut="$(uname -s)"
case "${unameOut}" in
    Linux*)     machine=Linux;;
    Darwin*)    machine=Mac;;
    CYGWIN*)    machine=Cygwin;;
    MINGW*)     machine=MinGw;;
    *)          machine="UNKNOWN:${unameOut}"
esac
${machine}

while true; do
    read -p "waiting command... " cmd
    if [ $cmd == "clean" ];
    then
        echo "Removing development sqlite databases"
        find . -name "*dev.sqlite*" -type f -delete
        echo "Removing notebooks outputs"
        find . -name "*output.ipynb" -type f -delete
        echo "Removing logs"
        find . -name "*.log*" -type f -delete
    # ======================================================================= #
    # Setup env
    # ======================================================================= #
    elif [ $cmd == "setup" ];
    then
        echo "Setup"
        python -m venv ~/environments/workflower
        echo "$(ls -lh ~/environments/workflower)"
    # ======================================================================= #
    # Run development environment
    # ======================================================================= #
    elif [ $cmd == "dev" ];
    then
        echo "Run dev"
        eval "$(cat .env.dev.template)"  && \
        python . init-db && \
        python . run
    # ======================================================================= #
    # Run tests environment
    # ======================================================================= #
    elif [ $cmd == "test" ];
    then
        echo "Run test"
        eval "$(cat .env.test.template)" && \
        python -m pytest -s tests/
    # ======================================================================= #
    # Run production environment
    # ======================================================================= #
    elif [ $cmd == "prod" ];
    then
        echo "Run prod"
        eval "$(cat .env.prod.template)"  && \
        python . run
    # ======================================================================= #
    # Run default .env environment
    # ======================================================================= #
    elif [ $cmd == "env" ];
    then
        echo "Run with .env"
        eval "$(cat .env)"  && \
        python . init-db && \
        python . run
    elif [ $cmd == "exit" ];
    then
        exit
    else
        echo "No arg received ending"
    fi
done