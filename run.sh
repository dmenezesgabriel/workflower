#!/bin/bash

set -e
# set -x # DEBUG
VERSION=0.1.0
NAME="CLI Helper"

ENV_PATH=~/environments/workflower
LINE_BREAK="################################################################\n"
CLI_WORKFLOWS_PATH=./samples/cli_standalone_workflows

bold_green_prefix="\033[1;32m"
bold_green_suffix="\033[00m"
bold_yellow_prefix="\033[1;33m"
bold_yellow_suffix="\033[00m"
yellow_prefix="\033[33m"
yellow_suffix="\033[00m"
red_prefix="\033[31m"
red_suffix="\033[00m"

greet() {
    ###########################################################################
    # Prompt Introduction
    ###########################################################################
    printf $LINE_BREAK
    echo -e "$bold_green_prefix"Hello "$(whoami)","$bold_green_suffix"
    echo "Welcome to $NAME, version $VERSION"
    printf $LINE_BREAK
    printf "\n"
}

prompt_help() {
    echo "Commands:"
    echo "- help: promp command options"
    echo "- setup: create $ENV_PATH"
    echo "- dev: init database and run app with dev config"
    echo "- prod: init database and run app with prod config"
    echo "- env: init database and run app with .env config"
    echo "- test: run tests"
    echo "- exit: exit program"
    printf "\n"
}

get_platform_function() {
    ###########################################################################
    # Get operational system
    ###########################################################################
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
    ###########################################################################
    # Create environment
    ###########################################################################
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
    ###########################################################################
    # Set venv paths
    ###########################################################################
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
    ###########################################################################
    # Install deps
    ###########################################################################
    echo "Installing python dependencies"
    eval "$(cat .env)"  && \
    $env_executable -m pip install -r requirements.txt
    $env_executable -m pip install -r requirements-plugins.txt
    $env_executable -m pip install -r requirements-dev.txt
}

build_docs() {
    ###########################################################################
    # Build docs
    ###########################################################################
    . $venv_activate && \
    sphinx-build ./docsrc/source ./docs
}

run_cli () {
    ###########################################################################
    # Run cli
    ###########################################################################
    printf "\n"
    echo "Starting CLI..."
    printf "\n"
    #  Get platform
    get_platform_function
    # env paths
    set_venv_paths
    # Prompt help
    printf "\n"
    greet
    prompt_help
    # Run

    while true; do
        read -p "$(echo -e $bold_yellow_prefix"Waiting command: "$bold_yellow_suffix)" cmd
        printf "\n"
        # =================================================================== #
        # Clean app data
        # =================================================================== #
        if [ $cmd == "help" ];
            then
                prompt_help
        elif [ $cmd == "clean" ];
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
                . $venv_activate && \
                playwright install
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
        # Run development environment
        # =================================================================== #
        elif [ $cmd == "docs" ];
            then
            build_docs
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
        # Standalone cli workflow
        # =================================================================== #
        elif [ $cmd == "workflow" ];
            then
                declare -A workflows_dict
                workflows_counter=0
                echo "Choose a workflow number: "
                printf "\n"
                for entry in "$CLI_WORKFLOWS_PATH"/*
                do
                let "workflows_counter+=1"
                workflows_dict["$workflows_counter"]="$entry"
                echo "$workflows_counter - $entry"
                done
                printf "\n"
                read -p "Workflow path: " workflow_number
                echo "Run with .env"
                . $venv_activate
                eval "$(cat .env)"  && \
                python . run_workflow --i "${workflows_dict[$workflow_number]}"
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
            echo -e "$red_prefix"Unreckognized arg, try again..."$red_suffix"
        fi
    done
}

# Start
run_cli