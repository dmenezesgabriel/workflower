import pytest
import workflower.loader as loader


def test_validate_true():
    configuration_dict = dict(
        version="1.0",
        workflow={
            "name": "workflow_name",
            "jobs": [
                {
                    "name": "job_name",
                    "uses": "job_uses",
                    "trigger": "job_trigger",
                },
            ],
        },
    )

    assert loader.validate_schema(configuration_dict) is True
