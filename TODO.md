# TODOs

- Dependency should not be an trigger type, but another definition in the pipeline, after workflow.
- Documentation
- Apply adapter, ports and domain design on models and orm.
- Plugins should use builder design pattern.
- Refactor schema validator to use strategy pattern as schema parser and move then to utils.
- Some times execution events seems to not be registered on database, investigate.
- Make database replication.
- Add alembic for database migrations
- Separate jobs from workflow to define dependencies as circleci ref:

  ```yml
  version: 2.1

  # Define the jobs we want to run for this project
  jobs:
  build:
      docker:
      - image: cimg/<language>:<version TAG>
          auth:
          username: mydockerhub-user
          password: $DOCKERHUB_PASSWORD # context / project UI env-var reference
      steps:
      - checkout
      - run: echo "this is the build job"
  test:
      docker:
      - image: cimg/<language>:<version TAG>
          auth:
          username: mydockerhub-user
          password: $DOCKERHUB_PASSWORD # context / project UI env-var reference
      steps:
      - checkout
      - run: echo "this is the test job"

  # Orchestrate our job run sequence
  workflows:
  build_and_test:
      jobs:
      - build
      - test:
          requires:
              - build
  ```

**Keep track of big files in commits**:

.twb
.json

- 5a7fe480540ebc6e83564a9dd26c0352961a6f2e
- 715459c3ee27c7fe529157a1977641f08b27fb24
