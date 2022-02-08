import os
import zipfile

from workflower.modules.module import BaseModule
from workflower.plugins.tableau_document import TableauDocumentPlugin


def extract_zipped_files(file_path, output_folder):
    with zipfile.ZipFile(file_path) as zip_ref:
        zip_ref.extractall(output_folder)


class Module(BaseModule):
    def __init__(self, plugins=[TableauDocumentPlugin()]) -> None:
        self._plugins = plugins

    def run(self):
        tableau_document_plugin = self.get_plugin("tableau_document_plugin")
        base_directory = (
            r"C:\Users\gabri\Documents\repos\workflower\samples\tableau"
        )
        workbooks_path = os.path.join(base_directory, "workbooks")
        _workbooks = []
        for root, dirs, files in os.walk(workbooks_path):
            print(root)
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
                workbook = tableau_document_plugin.create_component(
                    "workbook", target_file
                )
                _workbooks.append(workbook)
        _rows = []
        for workbook in _workbooks:
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
                                counter = 0
                                for run in runs:
                                    _row = dict()
                                    _row.update(
                                        dict(
                                            workbook_name=workbook.name,
                                            worksheet_name=worksheet.name,
                                            bold=run.bold,
                                            underline=run.underline,
                                            fontname=run.fontname,
                                            fontsize=run.fontsize,
                                            fontcolor=run.fontcolor,
                                            fontalignment=run.fontalignment,
                                        )
                                    )
                                    counter += 1
                                    _row[
                                        f"title_block_{counter}"
                                    ] = run.content
                                    _rows.append(_row)
            print(_rows)
