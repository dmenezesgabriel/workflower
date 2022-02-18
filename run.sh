#!/bin/bash

set -e
# set -x # DEBUG
VERSION=0.1.0
NAME="CLI Helper"

ENV_PATH=~/environments/workflower

prompt_help() {
    # ======================================================================= #
    # Prompt Introduction
    # ======================================================================= #
    echo "==========================================================="
    echo "Hello $(whoami),"
    echo "Welcome to $NAME, version $VERSION"
    echo "==========================================================="
    echo "Commands:"
    echo "- setup: create $ENV_PATH"
    echo "- dev: init database and run app with dev config"
    echo "- prod: init database and run app with prod config"
    echo "- env: init database and run app with .env config"
    echo "- test: run tests"
    echo "- exit: exit program"
    echo "==========================================================="
}

get_platform_function() {
    # ======================================================================= #
    # Get operational system
    # ======================================================================= #
    unameOut="$(uname -s)"
    case "${unameOut}" in
        Linux*)     machine=Linux;;
        Darwin*)    machine=Mac;;
        CYGWIN*)    machine=Cygwin;;
        MINGW*)     machine=MinGw;;
        *)          machine="UNKNOWN:${unameOut}"
    esac
}

create_env() {
    # ======================================================================= #
    # Create environment
    # ======================================================================= #
    echo "Creating python virtual environment"
    if [ $machine == "MinGw" ];
        then
            echo "Create venv on windows"
            py -3 -m venv $ENV_PATH
            env_executable=$ENV_PATH/Scripts/python
            venv_activate=$ENV_PATH/Scripts/activate
    elif [ $machine == "Linux" ];
        then
            echo "Create venv on linux"
            python -m venv $ENV_PATH
            env_executable=$ENV_PATH/bin/python
            venv_activate=$ENV_PATH/bin/activate
    else
        echo "Unreckognized arg, try again..."
    fi
}

set_venv_paths() {
    # ======================================================================= #
    # Set venv paths
    # ======================================================================= #
    echo "Setting venv paths"
    if [ $machine == "MinGw" ];
        then
            echo "Setting env paths on windows"
            env_executable=$ENV_PATH/Scripts/python
            venv_activate=$ENV_PATH/Scripts/activate
    elif [ $machine == "Linux" ];
        then
            echo "Setting env paths on linux"
            env_executable=$ENV_PATH/bin/python
            venv_activate=$ENV_PATH/bin/activate
    else
        echo "Unreckognized arg, try again..."
    fi
}

install_deps() {
    # ======================================================================= #
    # Install deps
    # ======================================================================= #
    echo "Installing python dependencies"
    $env_executable -m pip install -r requirements.txt
    $env_executable -m pip install -r requirements-plugins.txt
    $env_executable -m pip install -r requirements-dev.txt
}

run_cli () {
    # ======================================================================= #
    # Run cli
    # ======================================================================= #
    # Prompt help
    echo "Starting CLI"
    prompt_help
    #  Get platform
    get_platform_function
    # env paths
    set_venv_paths
    # Run
    while true; do
        read -p "waiting command... " cmd
        # =================================================================== #
        # Clean app data
        # =================================================================== #
        if [ $cmd == "clean" ];
            then
                echo "Removing development sqlite databases"
                find . -name "*dev.sqlite*" -type f -delete
                find . -name "*temp.sqlite*" -type f -delete
                echo "Removing notebooks outputs"
                find . -name "*output.ipynb" -type f -delete
                echo "Removing logs"
                find . -name "*.log*" -type f -delete
        # =================================================================== #
        # Setup env
        # =================================================================== #
        elif [ $cmd == "setup" ];
            then
                echo "Setup"
                create_env
                echo "$(ls -lh $ENV_PATH)"
                install_deps
        # =================================================================== #
        # Run development environment
        # =================================================================== #
        elif [ $cmd == "dev" ];
            then
                echo "Run dev"
                . $venv_activate
                eval "$(cat .env.dev.template)"  && \
                python -c"import sys; sys.executable"
                python . init-db && \
                python . run
        # =================================================================== #
        # Run tests environment
        # =================================================================== #
        elif [ $cmd == "test" ];
            then
                echo "Run test"
                . $venv_activate
                eval "$(cat .env.test.template)" && \
                python -m pytest -s tests/
        # =================================================================== #
        # Run production environment
        # =================================================================== #
        elif [ $cmd == "prod" ];
            then
                echo "Run prod"
                . $venv_activate
                eval "$(cat .env.prod.template)"  && \
                python . run
        # =================================================================== #
        # Run default .env environment
        # =================================================================== #
        elif [ $cmd == "env" ];
            then
                echo "Run with .env"
                . $venv_activate
                eval "$(cat .env)"  && \
                python . init-db && \
                python . run
        # =================================================================== #
        # Exit program
        # =================================================================== #
        elif [ $cmd == "exit" ];
            then
                exit
        # =================================================================== #
        # Unreckognized command
        # =================================================================== #
        else
            echo "Unreckognized arg, try again..."
        fi
    done
}

# Start
run_cli