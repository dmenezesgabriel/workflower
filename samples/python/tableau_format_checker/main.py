import os

import pandas as pd
import tableauserverclient as TSC

from loader import Loader

TABLEAU_USERNAME = os.getenv("TABLEAU_USERNAME")
TABLEAU_PASSWORD = os.getenv("TABLEAU_PASSWORD")
TABLEAU_SITENAME = os.getenv("TABLEAU_SITENAME")
TABLEAU_SERVER_URL = os.getenv("TABLEAU_SERVER_URL")
PROJECT_NAME = os.getenv("PROJECT_NAME")

base_directory = r"C:\Users\gabri\Documents\repos\workflower\samples\python\tableau_format_checker"
workbooks_path = os.path.join(base_directory, "workbooks")


if __name__ == "__main__":
    if not os.path.isdir(workbooks_path):
        os.makedirs(workbooks_path)

    tableau_auth = TSC.TableauAuth(
        username=TABLEAU_USERNAME,
        password=TABLEAU_PASSWORD,
        site=TABLEAU_SITENAME,
    )

    server = TSC.Server(TABLEAU_SERVER_URL)
    server.add_http_options({"verify": False})

    with server.auth.sign_in(tableau_auth):
        all_workbooks = TSC.Pager(server.workbooks)
        workbooks_dict = [
            {
                "workbook_id": workbook.id,
                "workbook_name": workbook.name,
                "workbook_project": workbook.project_name,
                "workbook_owner": workbook.owner_id,
            }
            for workbook in all_workbooks
            if workbook.project_name in PROJECT_NAME
        ]

    with server.auth.sign_in(tableau_auth):
        for workbook in workbooks_dict:
            server.workbooks.download(
                workbook_id=workbook["id"], filepath=workbooks_path
            )

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
