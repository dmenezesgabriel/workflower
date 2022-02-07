import os

import pandas as pd

from loader import Loader

base_directory = r"C:\Users\gabri\Documents\repos\workflower\samples\python\tableau_format_checker"
workbooks_path = os.path.join(base_directory, "workbooks")


if __name__ == "__main__":
    loader = Loader()
    loader.load_all(workbooks_path)
    print(loader.workbooks)
    _rows = []
    for workbook in loader.workbooks:
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
                                _row[f"title_block_{counter}"] = run.content
                                _rows.append(_row)
    _df = pd.DataFrame(_rows)
    print(_df)
