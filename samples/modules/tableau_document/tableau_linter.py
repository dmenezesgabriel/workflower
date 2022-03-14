import os
import zipfile

import pandas as pd
from workflower.modules.module import BaseModule


def extract_zipped_files(file_path, output_folder):
    with zipfile.ZipFile(file_path) as zip_ref:
        zip_ref.extractall(output_folder)


class Module(BaseModule):
    __name__ = "tableau_linter"

    def __init__(self, plugins) -> None:
        super().__init__(plugins)

    def run(self, *args, **kwargs):
        # Load plugins
        tableau_document_plugin = self.get_plugin("tableau_document_plugin")
        #  Define directories
        base_directory = "samples/tableau"
        workbooks_directory = os.path.join(base_directory, "workbooks")
        output_directory = os.path.join(base_directory, "output")

        # Makedirs

        if not os.path.isdir(output_directory):
            os.makedirs(output_directory)

        # Gather workbooks
        _workbooks = []
        counter = 0
        # Try twice in case of stranger things
        while counter < 2:
            counter += 1
            for root, dirs, files in os.walk(workbooks_directory):
                for file in files:
                    file_path = os.path.join(root, file)
                    if file_path.endswith(".twb"):
                        workbook = tableau_document_plugin.create_component(
                            "workbook", file_path
                        )
                        _workbooks.append(workbook)

        # Parse Workbooks
        _rows = []
        workbooks = set(_workbooks)
        for workbook in workbooks:
            for worksheet in workbook.worksheets:
                print(worksheet)
                layout_options = worksheet.layout_options
                if layout_options:
                    print(layout_options)
                    title = layout_options.title
                    if title:
                        print(title)
                        formatted_text = title.formatted_text
                        if formatted_text:
                            print(formatted_text)
                            runs = formatted_text.run
                            if runs:
                                for run in runs:
                                    _row = dict(
                                        workbook_name=workbook.name,
                                        worksheet_name=worksheet.name,
                                        bold=run.bold,
                                        underline=run.underline,
                                        fontname=run.fontname,
                                        fontsize=run.fontsize,
                                        fontcolor=run.fontcolor,
                                        fontalignment=run.fontalignment,
                                        type="worksheet_title_part",
                                        content=run.content,
                                    )
                                    _rows.append(_row)
        _df = pd.DataFrame(_rows)
        print(_df.head())
