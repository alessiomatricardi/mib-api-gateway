import base64
import json
import requests
import datetime
from typing import List
from mib import app
from mib.rao.messages import ReceivedMessage, PendingDeliveredMessage, DraftMessage

class MessageManager:
    
    MESSAGES_ENDPOINT = app.config['MESSAGES_MS_URL']
    USERS_ENDPOINT = app.config['USERS_MS_URL']
    REQUESTS_TIMEOUT_SECONDS = app.config['REQUESTS_TIMEOUT_SECONDS']

    @classmethod
    def get_bottlebox(cls, requester_id : int, label : str):
        url = "%s/bottlebox/%s" % (cls.MESSAGES_ENDPOINT, label)
        response = requests.get(
            url,
            json={
                'requester_id' : requester_id, 
            },
            timeout=cls.REQUESTS_TIMEOUT_SECONDS
        )

        if response.status_code == 200:
            
            json_payload = response.json()
            messages_json : List[dict] = json_payload['messages']
            messages = list()

            if label in ['pending', 'delivered']:
                messages = [PendingDeliveredMessage.build_from_json(message_json) for message_json in messages_json]
            elif label == 'received':
                messages = [ReceivedMessage.build_from_json(message_json) for message_json in messages_json]
            elif label == 'drafts':
                messages = [DraftMessage.build_from_json(message_json) for message_json in messages_json]
            
            return messages, 200
        
        else:
            return None, response.status_code  
    
    @classmethod
    def get_message_details(cls, requester_id: int, message_id: int, label: str):
        '''
        TODO commenta
        '''
        url = "%s/messages/%s/%s" % (cls.MESSAGES_ENDPOINT, str(label),str(message_id))
        response = requests.get(
            url,
            json={
                'requester_id'  : requester_id, 
            },
            timeout=cls.REQUESTS_TIMEOUT_SECONDS
        )

        if response.status_code != 200:
            return None, response.status_code

        json_payload = response.json()
        message_json : dict = json_payload['message']
        message = None

        if label in ['pending', 'delivered']:
            message = PendingDeliveredMessage.build_from_json(message_json)
        elif label == 'received':
            message = ReceivedMessage.build_from_json(message_json)
        elif label == 'drafts':
            message = DraftMessage.build_from_json(message_json)
        
        return message, 200
    
    @classmethod
    def send_message(cls, requester_id : int, deliver_time:str, content:str, recipients:list, is_draft:bool, imageb64:str, file_name:str):
        # gives a message to the MS 

        json_data                   = {}
        # take message content
        json_data['requester_id']   = requester_id
        json_data['deliver_time']   = deliver_time
        json_data['content']        = content
        json_data['recipients']     = recipients
        json_data['is_draft']       = is_draft
        json_data['image']          = imageb64
        json_data['image_filename'] = file_name


        url = "%s/messages" % cls.MESSAGES_ENDPOINT
        response = requests.post(
            url,
            json = json_data,
            timeout = cls.REQUESTS_TIMEOUT_SECONDS
        )

        return response.status_code

    @classmethod
    def get_attachment(cls, requester_id : int, label : str, message_id : int):

        url = "%s/messages/%s/%s/attachment" % (cls.MESSAGES_ENDPOINT, str(label),str(message_id))
        response = requests.get(
            url,
            json={
                'requester_id'  : requester_id, 
            },
            timeout=cls.REQUESTS_TIMEOUT_SECONDS
        )

        if response.status_code != 200:
            return None, None, response.status_code
        
        response_json = response.json()

        image_base64 = response_json['image']
        image_filename = response_json['image_filename']

        return image_base64, image_filename, 200

    @classmethod
    def modify_draft(cls, message_id : int, json_data : dict):

        url = "%s/messages/drafts/%s" % (cls.MESSAGES_ENDPOINT, str(message_id))
        response = requests.put(
            url,
            json = json_data,
            timeout = cls.REQUESTS_TIMEOUT_SECONDS
        )

        return response.status_code

    @classmethod
    def delete_message(cls, requester_id : int, label : str, message_id : int):

        url = "%s/messages/%s/%s" % (cls.MESSAGES_ENDPOINT, label, str(message_id))
        response = requests.delete(
            url,
            json = {
                'requester_id' : requester_id
            },
            timeout = cls.REQUESTS_TIMEOUT_SECONDS
        )

        return response.json()['description'], response.status_code

    @classmethod
    def report_message(cls, requester_id : int, message_id : int):
        url = "%s/messages/received/%s/report" % (cls.MESSAGES_ENDPOINT, str(message_id))
        response = requests.put(
            url,
            json = {
                'requester_id' : requester_id
            },
            timeout = cls.REQUESTS_TIMEOUT_SECONDS
        )

        return response.status_code

    @classmethod
    def hide_message(cls, requester_id : int, message_id : int):
        url = "%s/messages/received/%s/hide" % (cls.MESSAGES_ENDPOINT, str(message_id))
        response = requests.put(
            url,
            json = {
                'requester_id' : requester_id
            },
            timeout = cls.REQUESTS_TIMEOUT_SECONDS
        )

        return response.status_code

    @classmethod
    def validate_datetime(cls, deliver_time):
        if deliver_time < datetime.datetime.now(): # check if the datetime is correct
            return datetime.datetime.now() # if it is set to a past day, it is sent with current datetime 
        return deliver_time
    
    @classmethod
    def convert_image(cls, file):
        '''
        Convert a given file in a base64 encoded string
        '''
        img_base64 = base64.encodebytes(file.stream.read()).decode('utf-8')

        return img_base64