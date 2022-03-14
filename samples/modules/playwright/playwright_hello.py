from workflower.application.modules.module import BaseModule

from playwright.sync_api import sync_playwright


class Module(BaseModule):
    def __init__(self, plugins=None) -> None:
        self._plugins = plugins

    def run(self, *args, **kwargs):
        with sync_playwright() as p:
            browser = p.chromium.launch()
            page = browser.new_page()
            page.goto("http://playwright.dev")
            print(50 * "=")
            print(page.title())
            print(50 * "=")
            browser.close()
