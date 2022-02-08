import os

import tableauserverclient as TSC
import urllib3

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

TABLEAU_SITENAME = os.getenv("TABLEAU_SITENAME")
TABLEAU_SERVER_URL = os.getenv("TABLEAU_SERVER_URL")
TABLEAU_SITE_ID = os.getenv("TABLEAU_SITE_ID")
TABLEAU_TOKEN_NAME = os.getenv("TABLEAU_TOKEN_NAME")
TABLEAU_TOKEN_VALUE = os.getenv("TABLEAU_TOKEN_VALUE")
TABLEAU_SITE_ID = os.getenv("TABLEAU_SITE_ID")

DOWNLOADS_DIR = (
    r"C:\Users\gabri\Documents\repos\workflower\samples\tableau\workbooks"
)
PROJECTS_LIST = []


def main():
    tableau_auth = TSC.PersonalAccessTokenAuth(
        TABLEAU_TOKEN_NAME, TABLEAU_TOKEN_VALUE, site_id=TABLEAU_SITE_ID
    )
    server = TSC.Server(TABLEAU_SERVER_URL, use_server_version=True)

    server.add_http_options(dict(verify=False))
    if not os.path.isdir(DOWNLOADS_DIR):
        os.makedirs(DOWNLOADS_DIR)

    with server.auth.sign(tableau_auth):
        all_workbooks = TSC.Pager(server.workbooks)
        workbooks_dict = []
        for workbook in all_workbooks:
            if PROJECTS_LIST:
                if workbook.project_name not in PROJECTS_LIST:
                    continue

            workbook_info = dict(
                workbook_id=workbook.id,
                workbook_name=workbook.name,
                project=workbook.project_name,
                owner_id=workbook.owner_id,
            )
            workbooks_dict.append(workbook_info)
            try:
                server.workbooks.download(
                    workbook.id, filepath=DOWNLOADS_DIR, no_extract=True
                )
            except Exception:
                continue


if __name__ == "__main__":
    main()
