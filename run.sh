#!/bin/bash

set -e
# set -x # DEBUG
VERSION=0.1.0
NAME="CLI Helper"

ENV_PATH=~/environments/workflower
LINE_BREAK="################################################################\n"

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
    echo "- workflow: run a single standalone workflow, see samples"
    echo "- test: run tests"
    echo "- clear: clear terminal"
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
    eval "$(cat .env)"
    if [[ -z "${PIP_INDEX_URL}" ]] && [[ -z"${PIP_TRUSTED_HOST}" ]];
        # PIP_INDEX_URL and PIP_TRUSTED_HOST not setted
        then
        echo "Installing python dependencies"
        $env_executable -m pip install -r requirements.txt
        $env_executable -m pip install -r requirements-plugins.txt
        $env_executable -m pip install -r requirements-dev.txt
    else
        # PIP_INDEX_URL and PIP_TRUSTED_HOST setted
        echo "Installing python dependencies with custom --index-url=${PIP_INDEX_URL} and --trusted-host=${PIP_TRUSTED_HOST}"
        $env_executable -m pip install -r requirements.txt --index-url=${PIP_INDEX_URL} --trusted-host=${PIP_TRUSTED_HOST}
        $env_executable -m pip install -r requirements-plugins.txt --index-url=${PIP_INDEX_URL} --trusted-host=${PIP_TRUSTED_HOST}
        $env_executable -m pip install -r requirements-dev.txt --index-url=${PIP_INDEX_URL} --trusted-host=${PIP_TRUSTED_HOST}
    fi
}

build_docs() {
    ###########################################################################
    # Build docs
    ###########################################################################
    . $venv_activate && \
    sphinx-build ./docs/source ./docs/_build
}

publish_docs() {
    ###########################################################################
    # Force build ghpages
    ###########################################################################
    eval "$(cat .env)"  && \
    curl \
        -H "Accept: application/vnd.github.v3+json" \
        -u ${GH_NAME}:${GH_TOKEN} -X POST \
        https://api.github.com/repos/${GH_NAME}/${GH_REPO}/pages/builds
}

set_standalone_workflows_path() {
    eval "$(cat .env.cli.template)"
    if [[ -z "${CLI_WORKFLOWS_PATH}" ]];
        then
        CLI_WORKFLOWS_PATH=./samples/cli_standalone_workflows
        echo "Setting standalone execution workflows path at ${CLI_WORKFLOWS_PATH}"
    else
        echo "Standalone workflows execution files at ${CLI_WORKFLOWS_PATH}"
    fi
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
                find . -name "*.sqlite*" -type f -delete
                find . -name "*dump.sql*" -type f -delete
                echo "Removing notebooks outputs"
                find . -name "*output.ipynb" -type f -delete
                echo "Removing logs"
                find . -name "*.log*" -type f -delete
                find . -name "*log.csv*" -type f -delete

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
        # Force build pages
        # =================================================================== #
        elif [ $cmd == "pages" ];
            then
            publish_docs
        # =================================================================== #
        # Run production environment
        # =================================================================== #
        elif [ $cmd == "prod" ];
            then
                echo "Run prod"
                . $venv_activate
                eval "$(cat .env.prod.template)"  && \
                python . init-db && \
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
                echo "Run with .env.cli.template"
                . $venv_activate
                # Set workflows path
                set_standalone_workflows_path
                # Make view
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
                read -p "Choose workflow: " workflow_number
                # Back to menu
                if [ $workflow_number == "exit" ];
                    then
                        clear
                else
                    #  Run workflow
                    eval "$(cat .env.cli.template)"  && \
                    python . init-db && \
                    python . run_workflow --i "${workflows_dict[$workflow_number]}"
                fi
        # =================================================================== #
        # Clear
        # =================================================================== #
        elif [ $cmd == "clear" ];
            then
                clear
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