#!/bin/bash
# =========================================================================== #
# Clean app data
# =========================================================================== #
set -e
# set -x # DEBUG
VERSION=0.1.0
NAME="CLI Helper"

echo "========================"
echo "Hello $(whoami)",
echo "Welcome to $NAME"
echo "========================"

if [ $1 == "clean" ];
then
    echo "Removing development sqlite databases"
    find . -name "*dev.sqlite*" -type f -delete
    echo "Removing notebooks outputs"
    find . -name "*output.ipynb" -type f -delete
    echo "Removing logs"
    find . -name "*.log*" -type f -delete
# =========================================================================== #
# Setup env
# =========================================================================== #
elif [ $1 == "setup" ];
then
    echo "Setup"
    python -m venv ~/environments/workflower
    echo "$(ls -lh ~/environments/workflower)"
# =========================================================================== #
# Run development environment
# =========================================================================== #
elif [ $1 == "dev" ];
then
    echo "Run dev"
    eval "$(cat .env.dev.template)"  && \
    python . init-db && \
    python . run
# =========================================================================== #
# Run tests environment
# =========================================================================== #
elif [ $1 == "test" ];
then
    echo "Run test"
    eval "$(cat .env.test.template)" && \
    python -m pytest -s tests/
# =========================================================================== #
# Run production environment
# =========================================================================== #
elif [ $1 == "prod" ];
then
    echo "Run prod"
    eval "$(cat .env.prod.template)"  && \
    python . run
# =========================================================================== #
# Run default .env environment
# =========================================================================== #
elif [ $1 == "env" ];
then
    echo "Run with .env"
    eval "$(cat .env)"  && \
    python . init-db && \
    python . run
else
    echo "No arg received ending"
fi
