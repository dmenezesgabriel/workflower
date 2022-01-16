# Cycle

Every configured `CYCLE` seconds do:

- [x] Search for YAML workflow configuration files on configured directory
- [x] Parse YAML workflow configuration files found
- [ ] Run user input validations and raise errors
- [ ] Write Workflows and it's respective jobs in database
- [ ] Verify if the job has dependencies
- [ ] If job has dependencies, _schedule_ execution on it's dependency job done **event**
- [ ] Verify if job should be schedule
- [x] Schedule job
- [x] Alteryx job's execution detail will be stored at database
- [ ] Papermill job's execution detail will be stored at database
- [x] Repeat unless stopped
