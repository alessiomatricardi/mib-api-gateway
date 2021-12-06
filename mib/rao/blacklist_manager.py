from mib import app

from flask import abort, json
import requests

BLACKLIST_ENDPOINT = app.config['BLACKLIST_MS_URL']
REQUESTS_TIMEOUT_SECONDS = app.config['REQUESTS_TIMEOUT_SECONDS']

class BlacklistManager:

    BLACKLIST_ENDPOINT = app.config['BLACKLIST_MS_URL']
    REQUESTS_TIMEOUT_SECONDS = app.config['REQUESTS_TIMEOUT_SECONDS']

    @classmethod
    def block(cls, blocked_user_id: int, requester_id: int):
        """
        This method contacts the blacklist microservice, which 
        add a new element to the user's blacklist.
        :param blocked_user_id: id of the user to block
               requester_id: blocking user's id
        :return: 201 if it is successfull
        """
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
    def unblock(cls, blocked_user_id: int, requester_id: int):
        """
        This method contacts the blacklist microservice, which 
        remove an user form the requester's blacklist.
        :param blocked_user_id: id of the blocked user
               requester_id: id of the requester
        :return: 202 if it is successfull
        """
        try:
            url = "%s/unblock" % BLACKLIST_ENDPOINT
            response = requests.delete(url,
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
    def retrieving_blacklist(cls, requester_id: int):
        """
        This method contact the blacklist microservice and 
        retrieves the blacklist of the requesting user.
        return: list of id of the blocked users.
        """
        try:
            url = "%s/blacklist" % cls.BLACKLIST_ENDPOINT
            response = requests.get(url,
                                        json={
                                            'requester_id': requester_id,     
                                        },
                                        timeout=cls.REQUESTS_TIMEOUT_SECONDS
                                        )

            if response.status_code == 200:
                blacklist = response.json()['blacklist']
                blacklist = json.loads(blacklist)
            
        except (requests.exceptions.ConnectionError, requests.exceptions.Timeout):
            return abort(500)

        return blacklist