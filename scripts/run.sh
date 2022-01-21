#!/bin/bash
if [ $1 == "clean" ];
then
    find . -name "*.sqlite" -type f -delete
    find . -name "*output.ipynb" -type f -delete
elif [ $1 == "dev" ];
then
    . .env.dev.template & \
    python init_db.py & \
    python .
elif [ $1 == "test" ];
then
    . .env.test.template & \
    python -m pytest -s tests/
else
    . .env.prod.template & \
    python .
fi
