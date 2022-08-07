"""Custom HTTPException classes that extend werkzeug.exceptions."""
from werkzeug.exceptions import Unauthorized, Forbidden

_REALM_ADMIN_USERS = "admin_users@aequus.it"


class ApiUnauthorized(Unauthorized):
    """Raise status code 401 with customizable WWW-Authenticate header."""

    def __init__(
        self,
        description="Unauthorized",
        role="unknown",
        error=None,
        error_description=None,
    ):
        self.description = description
        self.www_auth_value = self.__get_www_auth_value(role, error, error_description)
        Unauthorized.__init__(
            self, description=description, response=None, www_authenticate=None
        )

    def get_headers(self, environ):
        return [("Content-Type", "text/html"), ("WWW-Authenticate", self.www_auth_value)]

    def __get_www_auth_value(self, role, error, error_description):
        realm = _REALM_ADMIN_USERS
        www_auth_value = f'Bearer realm="{realm}"'
        if error:
            www_auth_value += f', error="{error}"'
        if error_description:
            www_auth_value += f', error_description="{error_description}"'
        return www_auth_value


class ApiForbidden(Forbidden):
    """Raise status code 403 with WWW-Authenticate header."""

    description = "You are not an authorized user"

    def get_headers(self, environ):
        return [
            ("Content-Type", "text/html"),
            (
                "WWW-Authenticate",
                f'Bearer realm="{_REALM_ADMIN_USERS}", '
                'error="insufficient_scope", '
                'error_description="You are not an authorized user"',
            ),
        ]