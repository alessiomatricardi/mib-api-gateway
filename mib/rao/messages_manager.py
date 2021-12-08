import base64
import json
import requests
import datetime

from io             import StringIO

from mib.auth.user  import User
from mib            import app

from flask_login    import logout_user
from flask          import abort





MESSAGES_ENDPOINT           = app.config['MESSAGES_MS_URL']
USERS_ENDPOINT              = app.config['USERS_MS_URL']
REQUESTS_TIMEOUT_SECONDS    = app.config['REQUESTS_TIMEOUT_SECONDS']

class MessageManager:
    
    MESSAGES_ENDPOINT           = app.config['MESSAGES_MS_URL']
    USERS_ENDPOINT              = app.config['USERS_MS_URL']
    REQUESTS_TIMEOUT_SECONDS    = app.config['REQUESTS_TIMEOUT_SECONDS']
    
    @classmethod
    def get_message_details(cls, requester_id: int, message_id: int, label: str):
        #searching messages in received
        url         = "%s/messages/%s/%s" % (cls.MESSAGES_ENDPOINT, str(label),str(message_id))
        response    = requests.get( url, #return a list of Message objects
                                    json={
                                        'requester_id'  : requester_id, 
                                    },
                                    timeout=cls.REQUESTS_TIMEOUT_SECONDS
                                    )

        if response.status_code != 200:
            return None     

        return response.json()
    
    @classmethod
    def send_message(cls, user_id:int, deliver_time:str, content:str, recipients:list, is_draft:bool, imageb64:str, file_name:str):
        # gives a message to the MS 

        json_data                   = {}
        # take message content
        json_data['requester_id']   = user_id
        json_data['deliver_time']   = deliver_time
        json_data['content']        = content
        json_data['recipients']     = recipients
        json_data['is_draft']       = is_draft
        json_data['image']          = imageb64
        json_data['image_filename'] = file_name


        url         = "%s/messages" % cls.MESSAGES_ENDPOINT
        response    = requests.post( url, #return a list of Message objects
                                    json    = json_data,
                                    timeout = cls.REQUESTS_TIMEOUT_SECONDS
                                    )

        if response.status_code != 200:
            return None     

        return response.json()


    @classmethod
    def validate_datetime(cls, deliver_time):
        if deliver_time < datetime.datetime.now(): # check if the datetime is correct
            return datetime.datetime.now() # if it is set to a past day, it is sent with current datetime 
        return deliver_time

    
    @classmethod
    # verify that the file passed from the html page is a picture (png, jpg, jpeg, gif)
    def validate_file(cls, file):
        if file and file.filename != '' and file.filename.split('.')[-1] in ['png', 'jpg', 'jpeg', 'gif', 'PNG', 'JPG', 'JPEG', 'GIF']:
            return True
        else:
            return False

    
    @classmethod
    #convert a given file in base64
    def convert_image(cls, file):
        return base64.encodebytes(open(file, 'rb').read())