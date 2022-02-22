"""
Schema parser.
"""
import logging
import os
from abc import ABC, abstractclassmethod

from workflower.config import Config

logger = logging.getLogger("workflower.schema.parser")


class ParseStrategyInterface(ABC):
    """
    Parse Strategy interface.
    """

    @abstractclassmethod
    def parse(self) -> None:
        pass


class ParseStrategy(ParseStrategyInterface):
    """
    Parse Strategy base class.
    """

    def parse(self) -> None:
        pass


class PipelineSchemaParser:
    """
    Pipeline Schema parser.
    """

    def parse_version(self, configuration_dict: dict) -> str:
        """
        Parse pipeline version.
        """
        return configuration_dict["version"]

    def parse_schema(self, configuration_dict: dict) -> str:
        """
        Parse Pipeline schema.
        """
        version = self.parse_version(configuration_dict)
        return version


class WorkflowSchemaParser:
    """
    Workflow Schema parser.
    """

    def _get_workflow_name(self, configuration_dict: dict) -> str:
        """
        Parse workflow name.
        """
        return configuration_dict["workflow"]["name"]

    def _get_workflow_jobs_dict(self, configuration_dict: dict) -> str:
        """
        Parse jobs dict.
        """
        return configuration_dict["workflow"]["jobs"]

    def parse_schema(self, configuration_dict: dict) -> tuple:
        """
        Parse Workflow schema.
        """
        workflow_name = self._get_workflow_name(configuration_dict)
        jobs_dict = self._get_workflow_jobs_dict(configuration_dict)
        return workflow_name, jobs_dict


class IntervalTriggerParseStrategy(ParseStrategy):
    """
    Interval trigger parse strategy.
    """

    def parse(self, configuration_dict) -> dict:
        """
        parse_job a dict with interval trigger options.
        """
        interval_int_options = [
            "weeks",
            "days",
            "hours",
            "minutes",
            "seconds",
            "jitter",
        ]

        interval_string_options = [
            "start_date",
            "end_date",
            "timezone",
        ]
        interval_int_options_dict = {
            interval_option: int(configuration_dict.get(interval_option))
            for interval_option in interval_int_options
            if configuration_dict.get(interval_option)
        }
        interval_string_options_dict = {
            interval_option: str(configuration_dict.get(interval_option))
            for interval_option in interval_string_options
            if configuration_dict.get(interval_option)
        }
        return {**interval_int_options_dict, **interval_string_options_dict}


class CronTriggerParseStrategy(ParseStrategy):
    """
    Cron trigger parse strategy.
    """

    def parse(self, configuration_dict) -> dict:
        """
        parse_job a dict with cron trigger options.
        """
        interval_int_or_string_options = [
            "year",
            "month",
            "day",
            "week",
            "day_of_week",
            "hour",
            "minute",
            "second",
        ]
        interval_string_options = [
            "start_date",
            "end_date",
            "timezone",
        ]
        interval_int_options = [
            "jitter",
        ]
        interval_int_or_string_options_dict = {
            interval_option: configuration_dict.get(interval_option)
            for interval_option in interval_int_or_string_options
            if configuration_dict.get(interval_option)
            and (
                isinstance(configuration_dict.get(interval_option), int)
                or isinstance(configuration_dict.get(interval_option), str)
            )
        }
        interval_int_options_dict = {
            interval_option: int(configuration_dict.get(interval_option))
            for interval_option in interval_int_options
            if configuration_dict.get(interval_option)
        }
        interval_string_options_dict = {
            interval_option: str(configuration_dict.get(interval_option))
            for interval_option in interval_string_options
            if configuration_dict.get(interval_option)
        }
        return {
            **interval_int_or_string_options_dict,
            **interval_int_options_dict,
            **interval_string_options_dict,
        }


class DateTriggerParseStrategy(ParseStrategy):
    """
    Date trigger parse strategy.
    """

    def parse(self, configuration_dict) -> dict:
        """
        parse_job a dict with date trigger options.
        """
        date_string_options = [
            "run_date",
            "timezone",
        ]

        date_string_options_dict = {
            date_option: str(configuration_dict.get(date_option))
            for date_option in date_string_options
            if configuration_dict.get(date_option)
        }
        return date_string_options_dict


class DependencyTriggerParseStrategy(ParseStrategy):
    """
    Dependency trigger parse strategy.
    """

    def parse(self, configuration_dict) -> dict:
        # Trigger "dependency" is not recognized by apscheduler, so it
        # must be removed from job definition
        configuration_dict.pop("trigger", None)


def _create_trigger_parse_strategy(trigger_option: str):
    """
    Trigger parse strategy factory.
    """
    strategies = dict(
        interval=IntervalTriggerParseStrategy(),
        cron=CronTriggerParseStrategy(),
        date=DateTriggerParseStrategy(),
        dependency=DependencyTriggerParseStrategy(),
    )
    return strategies[trigger_option]


class JobTriggerSchemaParser:
    """
    Job Trigger Schema Context.
    """

    def __init__(self, strategy: ParseStrategy) -> None:
        self._strategy = strategy

    @property
    def strategy(self):
        return self._strategy

    @strategy.setter
    def strategy(self, strategy: ParseStrategy):
        self._strategy = strategy

    def parse(self, configuration_dict: dict):
        job_trigger = configuration_dict.get("trigger")
        trigger_options = self._strategy.parse(configuration_dict)
        if trigger_options:
            return dict(trigger=job_trigger, **trigger_options)
        else:
            return {}


class AlteryxOperatorParseStrategy(ParseStrategy):
    """
    Alteryx operator parse strategy.
    """

    def __init__(self) -> None:
        self.operator_config = {}
        self.schema_args = []
        self.schema_kwargs = {}

    def parse(self, configuration_dict: dict) -> dict:
        workflow_file_path = configuration_dict.get("path")
        if not os.path.isfile(workflow_file_path):
            logger.error("Not a valid job path")
        self.schema_kwargs.update(dict(workflow_file_path=workflow_file_path))
        self.operator_config.update(dict(func="AlteryxOperator.execute"))
        result_dict = dict()
        if self.operator_config:
            result_dict.update(self.operator_config)
        if self.schema_args:
            result_dict.update(dict(args=self.schema_args))
        if self.schema_kwargs:
            result_dict.update(dict(kwargs=self.schema_kwargs))
        return result_dict


class PapermillOperatorParseStrategy(ParseStrategy):
    """
    Papermill operator parse strategy.
    """

    def __init__(self) -> None:
        self.operator_config = {}
        self.schema_args = []
        self.schema_kwargs = {}

    def parse(self, configuration_dict: dict) -> dict:
        input_path = configuration_dict.get("input_path")
        if not os.path.isfile(input_path):
            logger.error("Not a valid job path")
        output_path = configuration_dict.get("output_path")
        self.operator_config.update(dict(func="PapermillOperator.execute"))
        self.schema_kwargs.update(
            dict(
                input_path=input_path,
                output_path=output_path,
                environments_dir=Config.ENVIRONMENTS_DIR,
                kernel_specs_dir=Config.KERNELS_SPECS_DIR,
                pip_index_url=Config.PIP_INDEX_URL,
                pip_trusted_host=Config.PIP_TRUSTED_HOST,
            )
        )
        result_dict = dict()
        if self.operator_config:
            result_dict.update(self.operator_config)
        if self.schema_args:
            result_dict.update(dict(args=self.schema_args))
        if self.schema_kwargs:
            result_dict.update(dict(kwargs=self.schema_kwargs))
        return result_dict


class PythonOperatorParseStrategy(ParseStrategy):
    """
    Python operator parse strategy.
    """

    def __init__(self) -> None:
        self.operator_config = {}
        self.schema_args = []
        self.schema_kwargs = {}

    def parse(self, configuration_dict: dict) -> dict:
        script_path = configuration_dict.get("script_path")
        code = configuration_dict.get("code")
        requirements_path = configuration_dict.get("requirements_path")
        if code:
            self.schema_kwargs.update(dict(code=code))
        elif script_path:
            if not os.path.isfile(script_path):
                logger.error("Not a valid python script path")
            self.schema_kwargs.update(dict(script_path=script_path))
        if requirements_path:
            if not os.path.isfile(requirements_path):
                logger.error("Not a valid requirements path")
            self.schema_kwargs.update(
                dict(requirements_path=requirements_path)
            )
        self.schema_kwargs.update(
            dict(
                pip_index_url=Config.PIP_INDEX_URL,
                pip_trusted_host=Config.PIP_TRUSTED_HOST,
                environments_dir=Config.ENVIRONMENTS_DIR,
            )
        )
        self.operator_config.update(dict(func="PythonOperator.execute"))
        result_dict = dict()
        if self.operator_config:
            result_dict.update(self.operator_config)
        if self.schema_args:
            result_dict.update(dict(args=self.schema_args))
        if self.schema_kwargs:
            result_dict.update(dict(kwargs=self.schema_kwargs))
        return result_dict


class ModuleOperatorParseStrategy(ParseStrategy):
    """
    Module operator parse strategy.
    """

    def __init__(self) -> None:
        self.operator_config = {}
        self.schema_args = []
        self.schema_kwargs = {}

    def parse(self, configuration_dict: dict) -> dict:
        module_path = configuration_dict.get("module_path")
        if not os.path.isfile(module_path):
            logger.error("Not a valid job path")
        module_name = configuration_dict.get("module_name")
        module_plugins = configuration_dict.get("plugins")
        self.operator_config.update(dict(func="ModuleOperator.execute"))
        self.schema_kwargs.update(
            dict(
                module_path=module_path,
                module_name=module_name,
                plugins=module_plugins,
            )
        )
        result_dict = dict()
        if self.operator_config:
            result_dict.update(self.operator_config)
        if self.schema_args:
            result_dict.update(dict(args=self.schema_args))
        if self.schema_kwargs:
            result_dict.update(dict(kwargs=self.schema_kwargs))
        return result_dict


class JobOperatorSchemaParser:
    """
    Job Use Schema Context.
    """

    def __init__(self, strategy: ParseStrategy) -> None:
        self._strategy = strategy

    @property
    def strategy(self):
        return self._strategy

    @strategy.setter
    def strategy(self, strategy: ParseStrategy):
        self._strategy = strategy

    def parse_operator(self, configuration_dict: dict):
        return self._strategy.parse(configuration_dict)


def _create_operator_parse_strategy(operator_option: str) -> ParseStrategy:
    """
    Operator strategy factory.
    """
    strategies = dict(
        alteryx=AlteryxOperatorParseStrategy(),
        papermill=PapermillOperatorParseStrategy(),
        python=PythonOperatorParseStrategy(),
        module=ModuleOperatorParseStrategy(),
    )
    return strategies[operator_option]


class JobSchemaParser:
    """
    Job Schema parser.
    """

    def _parse_job_trigger(self, configuration_dict: dict) -> dict:
        """
        Define trigger options from dict.
        """
        job_trigger = configuration_dict.get("trigger")
        logger.debug(f"Job trigger {job_trigger}")
        trigger_parser = JobTriggerSchemaParser(
            _create_trigger_parse_strategy(job_trigger)
        )
        return trigger_parser.parse(configuration_dict)

    def _parse_job_operator(self, configuration_dict: dict) -> dict:
        """
        Define job operator from dict.
        """
        job_operator = configuration_dict.get("operator")
        logger.debug(f"Job trigger {job_operator}")
        operator_parser = JobOperatorSchemaParser(
            _create_operator_parse_strategy(job_operator)
        )
        return operator_parser.parse_operator(configuration_dict)

    def parse_schema(self, configuration_dict: dict) -> tuple:
        """
        Parse Job schema.
        """
        job_name = configuration_dict.get("name")
        job_operator = configuration_dict.get("operator")
        job_depends_on = configuration_dict.get("depends_on", None)
        if job_depends_on:
            dependency_logs_pattern = configuration_dict.get(
                "dependency_logs_pattern", None
            )
            run_if_pattern_match = configuration_dict.get(
                "run_if_pattern_match", None
            )
        else:
            dependency_logs_pattern = None
            run_if_pattern_match = None
        job_trigger_options = self._parse_job_trigger(configuration_dict)
        job_operator_options = self._parse_job_operator(configuration_dict)
        job_config = dict(
            executor="default", **job_trigger_options, **job_operator_options
        )
        return (
            job_name,
            job_operator,
            job_depends_on,
            dependency_logs_pattern,
            run_if_pattern_match,
            job_config,
        )
