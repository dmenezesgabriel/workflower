import logging
import os
import zipfile

from workflower.modules.module import BaseModule


def extract_zipped_files(file_path, output_folder):
    with zipfile.ZipFile(file_path) as zip_ref:
        zip_ref.extractall(output_folder)


# TODO
# Make logger part of base module
logger = logging.getLogger("workflower.modules.tableau_linter")


class Module(BaseModule):
    def __init__(self, plugins=None) -> None:
        self._plugins = plugins

    def run(self, *args, **kwargs):
        #  Define directories
        base_directory = "samples/tableau"
        workbooks_directory = os.path.join(base_directory, "workbooks")

        # Itereate through workbooks dir
        for root, dirs, files in os.walk(workbooks_directory):
            for file in files:
                file_path = os.path.join(root, file)
                base_file_name = (
                    os.path.splitext(os.path.basename(file_path))[0]
                    .replace(" ", "_")
                    .lower()
                )
                if file_path.endswith(".twb"):
                    continue
                elif file_path.endswith(".twbx"):
                    extraction_output_path = os.path.join(
                        workbooks_directory, "unzipped", base_file_name
                    )
                    extract_zipped_files(file_path, extraction_output_path)
