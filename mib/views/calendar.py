from flask import Blueprint, render_template, abort
from flask_login.utils import login_required
from flask_login import current_user
from mib.rao.messages_manager import MessageManager
import json

calendar = Blueprint('calendar', __name__)


@calendar.route('/calendar',methods=['GET'])
@login_required
def _which_calendar():
    return render_template('which_calendar.html')


@calendar.route('/calendar/sent',methods=['GET'])
@login_required
def _show_calendar_of_sent_messages():
    
    pending_messages, status_code = MessageManager.get_bottlebox(current_user.id, 'pending')

    delivered_messages, status_code2 = MessageManager.get_bottlebox(current_user.id, 'delivered')

    if status_code != 200 or status_code2 != 200:
        abort(status_code)
    
    sent = []
    for message in pending_messages:
        for recipient in message.recipients:
            message_json = {
                "id" : message.id,
                "deliver_time" : message.deliver_time.strftime('%Y-%m-%dT%H:%M'),
                "title" : "Message to %s %s (%s)" % (recipient.firstname, recipient.lastname, recipient.email),
                "type" : 'pending'
            }
        
            sent.append(message_json)
    
    for message in delivered_messages:
        for recipient in message.recipients:
            message_json = {
                "id" : message.id,
                "deliver_time" : message.deliver_time.strftime('%Y-%m-%dT%H:%M'),
                "title" : "Message to %s %s (%s)" % (recipient.firstname, recipient.lastname, recipient.email),
                "type" : 'delivered'
            }
        
            sent.append(message_json)

    return render_template('calendar.html', messages = sent)



@calendar.route('/calendar/received',methods=['GET'])
@login_required
def _show_calendar_of_received_messages():
    
    received_messages, status_code = MessageManager.get_bottlebox(current_user.id, 'received')

    if status_code != 200:
        abort(status_code)

    received = []
    for message in received_messages:
        message_json = {
            "id" : message.id,
            "deliver_time" : message.deliver_time.strftime('%Y-%m-%dT%H:%M'),
            "title" : "Message from %s %s (%s)" % (message.sender_firstname, message.sender_lastname, message.sender_email),
            "type" : 'received'
        }
        
        received.append(message_json)

    return render_template('calendar.html', messages = received)