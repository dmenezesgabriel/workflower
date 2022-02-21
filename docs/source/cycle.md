# Cycle

Every configured `CYCLE` seconds do

- [x] Search for YAML workflow configuration files on configured directory
- [x] Load workflows
- [x] Parse YAML workflow configuration files found
- [x] Run user input validations and raise errors if not compliant
- [x] Write Workflows and it's respective jobs in database
- [x] Write App events on database.
- [x] Verify if the job has dependencies
- [x] If job has dependencies, _schedule_ execution on it's dependency job done **event**
- [x] Schedule job
- [x] Alteryx job's execution detail will be stored at database
- [x] Papermill job's execution detail will be stored at database
- [x] Python job's execution detail will be stored at database
- [x] Repeat unless stopped
