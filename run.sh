#!/bin/bash
if [ $1 == "clean" ];
then
    echo "Removing development sqlite databases"
    find . -name "*dev.sqlite" -type f -delete
    echo "Removing notebooks outputs"
    find . -name "*output.ipynb" -type f -delete
    echo "Removing logs"
    find . -name "*.log*" -type f -delete
elif [ $1 == "dev" ];
then
    echo "Run dev"
    eval "$(cat .env.dev.template)"  && \
    python init_db.py && \
    python .
elif [ $1 == "test" ];
then
    echo "Run test"
    eval "$(cat .env.test.template)" && \
    python -m pytest -s tests/
elif [ $1 == "prod" ];
then
    echo "Run prod"
    eval "$(cat .env.prod.template)"  && \
    python .
else
    echo "No arg received ending"
fi
