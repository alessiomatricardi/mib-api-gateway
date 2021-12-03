import base64
from mib.auth.user import User
from mib import app
from flask_login import logout_user
from flask import abort
import requests

USERS_ENDPOINT = app.config['USERS_MS_URL']
REQUESTS_TIMEOUT_SECONDS = app.config['REQUESTS_TIMEOUT_SECONDS']

class UserManager:

    @classmethod
    def get_user_by_id(cls, user_id: int) -> User:
        """
        This method contacts the users microservice
        and retrieves the user object by user id.
        :param user_id: the user id
        :return: User obj with id=user_id
        """
        try:
            json = {'requester_id' : user_id}
            response = requests.get("%s/users/%s" % (USERS_ENDPOINT, str(user_id)),
                                    timeout=REQUESTS_TIMEOUT_SECONDS,
                                    json = json)
            json_payload = response.json()['user']

            if response.status_code == 200:
                # user is authenticated
                user = User.build_from_json(json_payload)
            else:
                raise RuntimeError('Server has sent an unrecognized status code %s' % response.status_code)

        except (requests.exceptions.ConnectionError, requests.exceptions.Timeout):
            return abort(500)

        return user

    # TODO QUESTO NON DOVREBBE ESSERE ESPOSTO ALL'UTENTE
    # AL MASSIMO DENTRO IL GATEWAY
    @classmethod
    def get_user_by_email(cls, user_email: str):
        """
        This method contacts the users microservice
        and retrieves the user object by user email.
        :param user_email: the user email
        :return: User obj with email=user_email
        """
        try:
            response = requests.get("%s/user_email/%s" % (USERS_ENDPOINT, user_email),
                                    timeout=REQUESTS_TIMEOUT_SECONDS)
            json_payload = response.json()
            user = None

            if response.status_code == 200:
                user = User.build_from_json(json_payload)

        except (requests.exceptions.ConnectionError, requests.exceptions.Timeout):
            return abort(500)

        return user

    @classmethod
    def register(cls,
                    email: str, password: str,
                    firstname: str, lastname: str,
                    birthdate):
        try:
            url = "%s/register" % USERS_ENDPOINT
            response = requests.post(url,
                                     json={
                                         'email': email,
                                         'password': password,
                                         'date_of_birth': birthdate,
                                         'firstname': firstname,
                                         'lastname': lastname,
                                     },
                                     timeout=REQUESTS_TIMEOUT_SECONDS
                                     )

        except (requests.exceptions.ConnectionError, requests.exceptions.Timeout):
            return abort(500)

        return response

    @classmethod
    def modify_data(cls, user_id: int, firstname: str, lastname: str, birthdate: str):
        """

        :return: User updated
        """
        try:
            url = "%s/profile/data" % USERS_ENDPOINT
            response = requests.patch(url,
                                    json={
                                        'requester_id': user_id,
                                        'firstname': firstname,
                                        'lastname': lastname,
                                        'date_of_birth': birthdate,
                                    },
                                    timeout=REQUESTS_TIMEOUT_SECONDS
                                    )
            return response

        except (requests.exceptions.ConnectionError, requests.exceptions.Timeout):
            return abort(500)

        raise RuntimeError('Error with searching for the user %s' % user_id)

    @classmethod
    def modify_password(cls, user_id: int, old_password: str, new_password: str, repeat_new_password: str):
        """

        :return: Password updated
        """
        try:
            url = "%s/profile/password" % USERS_ENDPOINT
            response = requests.patch(url,
                                    json={
                                        'requester_id': user_id,
                                        'old_password': old_password,
                                        'new_password': new_password,
                                        'repeat_new_password': repeat_new_password,
                                    },
                                    timeout=REQUESTS_TIMEOUT_SECONDS
                                    )
            return response

        except (requests.exceptions.ConnectionError, requests.exceptions.Timeout):
            return abort(500)

        raise RuntimeError('Error with searching for the user %s' % user_id)

    @classmethod
    def unregister(cls,
                    user_id: int,
                    password: str,
                    ):
        try:
            url = "%s/unregister" % USERS_ENDPOINT
            response = requests.put(url,
                                     json={
                                         'requester_id': user_id,
                                         'password': password,
                                     },
                                     timeout=REQUESTS_TIMEOUT_SECONDS
                                     )

        except (requests.exceptions.ConnectionError, requests.exceptions.Timeout):
            return abort(500)

        return response

    @classmethod
    def login_user(cls, email: str, password: str):
        """
        This method authenticates the user trough users AP
        :param email: user email
        :param password: user password
        :return: None if credentials are not correct, User instance if credentials are correct.
        """
        payload = dict(email=email, password=password)
        try:
            response = requests.post('%s/login' % USERS_ENDPOINT,
                                     json=payload,
                                     timeout=REQUESTS_TIMEOUT_SECONDS
                                     )
            json_response = response.json()
        except (requests.exceptions.ConnectionError, requests.exceptions.Timeout):
            # We can't connect to Users MS
            return abort(500)

        status_code = response.status_code

        # user doesn't exist or is not authenticated
        if status_code in [401, 404]:
            return None, status_code
        elif status_code == 200:
            user = User.build_from_json(json_response['user'])
            return user, status_code
        else:
            raise RuntimeError(
                'Microservice users returned an invalid status code %s, and message %s'
                % (response.status_code, json_response['error_message'])
            )

    @classmethod
    def modify_content_filter(cls, user_id: str, enabled: bool):
        try:
            url = "%s/profile/content_filter" % USERS_ENDPOINT
            response = requests.patch(url,
                                        json={
                                            'requester_id': user_id,
                                            'content_filter': enabled,
                                        },
                                        timeout=REQUESTS_TIMEOUT_SECONDS
                                        )

        except (requests.exceptions.ConnectionError, requests.exceptions.Timeout):
            return abort(500)

        return response

    @classmethod
    def modify_profile_picture(cls, user_id: str, image: base64):
        try:
            url = "%s/profile/picture" % USERS_ENDPOINT
            response = requests.put(url,
                                        json={
                                            'requester_id': user_id,
                                            'image': image,
                                        },
                                        timeout=REQUESTS_TIMEOUT_SECONDS
                                        )

        except (requests.exceptions.ConnectionError, requests.exceptions.Timeout):
            return abort(500)

        return response