import tableauserverclient as TSC
from workflower.plugins.tableau_server import (
    TABLEAU_SERVER_URL,
    TABLEAU_SITE_ID,
    TABLEAU_TOKEN_NAME,
    TABLEAU_TOKEN_VALUE,
)
from workflower.plugins.tableau_server.auth import AuthHelper


class ServerManager:
    def __init__(self) -> None:
        self._server = TSC.Server(TABLEAU_SERVER_URL, use_server_version=True)
        self._server

    @property
    def server(self):
        return self._server

    def apply_server_options(self, options_dict):
        self._server.add_http_options(options_dict)

    def sigin_in(self):
        tableau_authentication = AuthHelper.create_auth(
            TABLEAU_TOKEN_NAME, TABLEAU_TOKEN_VALUE, TABLEAU_SITE_ID
        )
        self._server.auth.sign_in(tableau_authentication)

    def sigin_out(self):
        self._server.auth.sign_out()
