#!/bin/bash
if [ $1 == "clean" ];
then
    find . -name "*.sqlite" -type f -delete
    find . -name "*output.ipynb" -type f -delete
elif [ $1 == "dev" ];
then
    eval "$(cat .env.dev.template)"  && \
    python init_db.py && \
    python .
elif [ $1 == "test" ];
then
    eval "$(cat .env.test.template)" && \
    python -m pytest -s tests/
else
    eval "$(cat .env.prod.template)"  && \
    python .
fi
