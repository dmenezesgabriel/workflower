import os

import requests
from workflower.application.modules.module import BaseModule

from playwright.sync_api import sync_playwright


class Module(BaseModule):
    def __init__(self, plugins=None) -> None:
        self._plugins = plugins

    def run(self, *args, **kwargs):
        downloads_dir = "./download"
        if not os.path.isdir(downloads_dir):
            os.makedirs(downloads_dir)

        with sync_playwright() as p:
            browser = p.chromium.launch()
            page = browser.new_page(accept_downloads=True)
            page.goto("https://public.tableau.com/en-us/s/resources")

            print(50 * "=")
            print(page.title())
            print(50 * "=")

            # HTTP Download
            for element in page.query_selector_all("a"):
                _href = element.get_attribute("href")
                if _href:
                    if _href.endswith(".csv"):
                        print(f"HREF: {_href} ")
                        request = requests.get(_href)
                        # remove special chars from file name in href
                        fname = "".join(
                            e
                            for e in _href.split("/")[-1]
                            if e.isalnum() or e == "."
                        )
                        file_path = os.path.join(downloads_dir, fname)
                        with open(file_path, "wb") as output:
                            output.write(request.content)
