import datetime
from re import split
from typing import List

class Message():
    '''
    This class is not a model, it is only a lightweight class used
    to represents a message.
    '''

    id = None
    content = None
    deliver_time = None
    sender_id = None
    image = None

    # A list of fields to be serialized
    SERIALIZE_LIST = ['id', 'content', 'deliver_time', 'sender_id','image']

    def __init__(self, **kw):
        if kw is None:
            raise RuntimeError('You can\'t build the message with none dict')
        self.id = kw["id"]
        self.content = kw["content"]
        date_time = kw['deliver_time'].split('T')
        date = date_time[0].split('-')
        time = date_time[1].split(':')
        self.deliver_time = datetime.datetime(int(date[0]), int(date[1]), int(date[2]), int(time[0]), int(time[1]))
        self.sender_id = kw["sender_id"]
        self.image = kw["image"]

class DraftMessage(Message):
    '''
    This class is not a model, it is only a lightweight class used
    to represents a draft message.
    '''
    
    recipients = None # recipients is a list of string objects

    # A list of fields to be serialized
    DRAFT_SERIALIZE_LIST = ['id', 'content', 'deliver_time', 'sender_id','image', 'recipients']

    @staticmethod
    def build_from_json(json: dict):
        kw = {key: json[key] for key in DraftMessage.DRAFT_SERIALIZE_LIST}

        return DraftMessage(**kw)

    def __init__(self, **kw):
        if kw is None:
            raise RuntimeError('You can\'t build the draft message with none dict')
        
        super().__init__(**kw)

        self.recipients = list()

        for recipient_email in kw['recipients']:
            self.recipients.append(recipient_email)
        
class ReceivedMessage(Message):
    '''
    This class is not a model, it is only a lightweight class used
    to represents a received message.
    '''
    
    is_read = False
    is_reported = False
    is_sender_active = False
    is_sender_in_blacklist = False
    sender_email = None
    sender_firstname = None
    sender_lastname = None

    # A list of fields to be serialized
    RECEIVED_SERIALIZE_LIST = ['id', 'content', 'deliver_time', 'sender_id', 'image', 'is_read', 'is_reported', 
                    'is_sender_active', 'is_sender_in_blacklist', 'sender_email', 'sender_firstname', 'sender_lastname']

    @staticmethod
    def build_from_json(json: dict):
        kw = {key: json[key] for key in ReceivedMessage.RECEIVED_SERIALIZE_LIST}

        return ReceivedMessage(**kw)

    def __init__(self, **kw):
        if kw is None:
            raise RuntimeError('You can\'t build the received message with none dict')
        
        super().__init__(**kw)
        
        self.is_read = kw["is_read"]
        self.is_reported = kw["is_reported"]
        self.is_sender_active = kw["is_sender_active"]
        self.is_sender_in_blacklist = kw["is_sender_in_blacklist"]
        self.sender_email = kw["sender_email"]
        self.sender_firstname = kw["sender_firstname"]
        self.sender_lastname = kw['sender_lastname']

class PendingDeliveredMessage(Message):
    '''
    This class is not a model, it is only a lightweight class used
    to represents a pending or delivered message.
    '''
    
    recipients = None # recipients is a list of Recipient objects

    # A list of fields to be serialized
    PENDING_SERIALIZE_LIST = ['id', 'content', 'deliver_time', 'sender_id','image', 'recipients']

    @staticmethod
    def build_from_json(json: dict):
        kw = {key: json[key] for key in PendingDeliveredMessage.PENDING_SERIALIZE_LIST}

        return PendingDeliveredMessage(**kw)

    def __init__(self, **kw):
        if kw is None:
            raise RuntimeError('You can\'t build the draft message with none dict')
        
        super().__init__(**kw)

        self.recipients = list()

        for recipient_json in kw['recipients']:
            recipient = Recipient.build_from_json(recipient_json)
            self.recipients.append(recipient)


class Recipient():
    '''
    This class is not a model, it is only a lightweight class used
    to represents a recipient of a pending or delivered message.
    '''
    
    id = None
    firstname = None
    lastname = None
    email = None
    is_in_blacklist = True

    # A list of fields to be serialized
    SERIALIZE_LIST = ['id', 'firstname', 'lastname', 'email', 'is_in_blacklist']

    @staticmethod
    def build_from_json(json: dict):
        kw = {key: json[key] for key in Recipient.SERIALIZE_LIST}

        return Recipient(**kw)

    def __init__(self, **kw):
        if kw is None:
            raise RuntimeError('You can\'t build the recipient with none dict')
        
        self.id = kw['id']
        self.firstname = kw['firstname']
        self.lastname = kw['lastname']
        self.email = kw['email']
        self.is_in_blacklist = kw['is_in_blacklist']