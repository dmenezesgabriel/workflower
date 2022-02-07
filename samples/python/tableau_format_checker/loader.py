import os
import zipfile

from tableau.workbook import Workbook


def extract_zipped_files(file_path, output_folder):
    with zipfile.ZipFile(file_path) as zip_ref:
        zip_ref.extractall(output_folder)


class Loader:
    def __init__(self) -> None:
        self._workbooks = None

    @property
    def workbooks(self):
        return self._workbooks

    def load_one(self, file_path):
        """
        Load one workbook from path.
        """
        return Workbook(file_path)

    def load_all(self, workbooks_path):
        """
        Load all workbooks from path.
        """
        self._workbooks = []
        for root, dirs, files in os.walk(workbooks_path):
            for file in files:
                file_path = os.path.join(root, file)
                base_file_name = (
                    os.path.splitext(os.path.basename(file_path))[0]
                    .replace(" ", "_")
                    .lower()
                )
                if file_path.endswith(".twb"):
                    target_path = root

                if file_path.endswith(".twbx"):
                    extraction_output_path = os.path.join(
                        workbooks_path, "unzipped", base_file_name
                    )
                    if not os.path.isdir(extraction_output_path):
                        extract_zipped_files(file_path, extraction_output_path)
                    target_path = extraction_output_path
                else:
                    continue

                new_file_extension = file.replace("twbx", "twb")
                target_file = os.path.join(target_path, new_file_extension)
                workbook = self.load_one(target_file)
                self._workbooks.append(workbook)
