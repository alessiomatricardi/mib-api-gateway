from mib import app
from flask_login import logout_user

from flask import abort
import requests

BLACKLIST_ENDPOINT = app.config['BLACKLIST_MS_URL']
REQUESTS_TIMEOUT_SECONDS = app.config['REQUESTS_TIMEOUT_SECONDS']

class BlacklistManager:

    BLACKLIST_ENDPOINT = app.config['BLACKLIST_MS_URL']
    REQUESTS_TIMEOUT_SECONDS = app.config['REQUESTS_TIMEOUT_SECONDS']

    @classmethod
    def block(cls, blocked_user_id: int, requester_id: int):

        try:
            url = "%s/block" % BLACKLIST_ENDPOINT
            response = requests.post(url,
                                        json={
                                            'requester_id': requester_id,
                                            'blocked_user_id': blocked_user_id,
                                        },
                                        timeout=REQUESTS_TIMEOUT_SECONDS
                                        )

        except (requests.exceptions.ConnectionError, requests.exceptions.Timeout):
            return abort(500)

        return response
    
    @classmethod
    def retrieving_blacklist(cls)