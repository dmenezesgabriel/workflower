import os
import zipfile

import pandas as pd
from workflower.application.modules.module import BaseModule


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

        for root, dirs, files in os.walk(workbooks_directory):
            for file in files:
                file_path = os.path.join(root, file)
                if file_path.endswith(".twb"):
                    workbook = tableau_document_plugin.create_component(
                        "workbook", file_path
                    )
                    _workbooks.append(workbook)

        # Parse Workbooks
        EXPECTED_FONT_NAME = "Tableau Book"
        EXPECTED_WORKSHEET_TITLE_FONT_SIZE = "12"
        EXPECTED_WORKSHEET_TITLE_FONT_COLOR = "#343a40"

        EXPECTED_DASHBOARD_HEIGHTS = ["768", "1800"]
        EXPECTED_DASHBOARD_WIDTH = "1200"

        workbooks = set(_workbooks)

        worksheet_validation_rows = []
        dashboard_validation_rows = []
        for workbook in workbooks:
            # Validate worksheets
            for worksheet in workbook.worksheets:
                layout_options = worksheet.layout_options
                title = layout_options.title if layout_options else None
                formatted_text = title.formatted_text if title else None
                runs = formatted_text.runs if formatted_text else None
                if runs:
                    for run in runs:
                        worksheet_validation_row = dict(
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
                            fontname_compliant=(
                                run.fontname == EXPECTED_FONT_NAME
                            ),
                            fontsize_compliant=(
                                run.fontsize
                                == EXPECTED_WORKSHEET_TITLE_FONT_SIZE
                            ),
                            fontcolor_compliant=(
                                run.fontcolor
                                == EXPECTED_WORKSHEET_TITLE_FONT_COLOR
                            ),
                        )
                        worksheet_validation_rows.append(
                            worksheet_validation_row
                        )

            # Validate dashboards
            for dashboard in workbook.dashboards:
                size = dashboard.size
                dashboard_validation_row = dict(
                    workbook_name=workbook.name,
                    maxheight=size.maxheight,
                    maxwidth=size.maxwidth,
                    minheight=size.minheight,
                    minwidth=size.minwidth,
                    maxheight_compliant=size.maxheight
                    in EXPECTED_DASHBOARD_HEIGHTS,
                    maxwidth_compliant=size.maxwidth
                    == EXPECTED_DASHBOARD_WIDTH,
                    minheight_compliant=size.minheight
                    in EXPECTED_DASHBOARD_HEIGHTS,
                    minwidth_compliant=size.minwidth
                    == EXPECTED_DASHBOARD_WIDTH,
                )
                dashboard_validation_rows.append(dashboard_validation_row)

        worksheet_validation_df = pd.DataFrame(worksheet_validation_rows)
        dashboard_validation_df = pd.DataFrame(dashboard_validation_rows)

        print(worksheet_validation_df.head())
        print(dashboard_validation_df.head())
