import tableauserverclient as TSC


class AuthHelper:
    @classmethod
    def create_auth(cls, tableau_token_name, tableau_token_value, site_id):
        """
        Create Tableau authentication.
        """
        return TSC.PersonalAccessTokenAuth(
            tableau_token_name,
            tableau_token_value,
            site_id=site_id,
        )
