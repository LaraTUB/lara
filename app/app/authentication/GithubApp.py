import jwt
import time
import json
from http.client import HTTPSConnection
from github import InstallationAuthorization, GithubException, Github


class GithubApp(object):
    """
    GithubApp class for authentication and managing installations
    Available endpoints:    https://developer.github.com/v3/apps/available-endpoints/
    """

    def __init__(self, integration_id, private_key):
        """
        :param integration_id: int
        :param private_key: string
        """
        self.integration_id = integration_id
        self.private_key = private_key

    def get_installation(self, installation_id):
        token = self._get_installation_access_token(installation_id)
        return Github(token)

    def _create_jwt(self):
        """
        Creates a signed JWT, valid for 60 seconds.
        :return:
        """
        now = int(time.time())
        payload = {
            "iat": now,
            "exp": now + 60,
            "iss": self.integration_id
        }
        return jwt.encode(
            payload,
            key=self.private_key,
            algorithm="RS256"
        )

    def _get_installation_access_token(self, installation_id):
        """
        Get an access token for the given installation id.
        POSTs https://api.github.com/installations/<installation_id>/access_tokens
        :param user_id: int
        :param installation_id: int
        :return: :class:`github.InstallationAuthorization.InstallationAuthorization`
        """
        conn = HTTPSConnection("api.github.com")
        conn.request(
            method="POST",
            url="/installations/{}/access_tokens".format(installation_id),
            headers={
                "Authorization": "Bearer {}".format(self._create_jwt().decode()),
                "Accept": "application/vnd.github.machine-man-preview+json",
                "User-Agent": "LaraTUB/lara"
            }
        )
        response = conn.getresponse()
        response_text = response.read()

        response_text = response_text.decode('utf-8')

        conn.close()
        if response.status == 201:
            data = json.loads(response_text)
            return InstallationAuthorization.InstallationAuthorization(
                requester=None,  # not required, this is a NonCompletableGithubObject
                headers={},  # not required, this is a NonCompletableGithubObject
                attributes=data,
                completed=True
            ).token
        elif response.status == 403:
            raise GithubException.BadCredentialsException(
                status=response.status,
                data=response_text
            )
        elif response.status == 404:
            raise GithubException.UnknownObjectException(
                status=response.status,
                data=response_text
            )
        raise GithubException.GithubException(
            status=response.status,
            data=response_text
        )
