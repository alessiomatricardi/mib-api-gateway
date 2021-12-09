import datetime
from flask import Blueprint, redirect, render_template, flash, request
from flask_login import login_required, current_user
from PIL import Image
from mib.forms.message import MessageForm
from mib.rao.user_manager import UserManager
from mib.rao.messages_manager import MessageManager
from mib.rao.messages import PendingDeliveredMessage, ReceivedMessage, Recipient

messages = Blueprint('messages', __name__)


@messages.route('/messages', methods=['GET', 'POST'])
@login_required
def _new_message():
    """
    This method allows to create and handle a new message
    """

    form = MessageForm()

    if request.method == 'GET':
        """
        GET request arguments
        {
            In case of a forward message:
            'forward'   : bool, Is this message a forwarded message?
            'label'     : string, The forwarded message is a received or delivered message?
            'message_id': int, message to forward

            OR

            In general
            'write_to : string, 
         }
        """
        message_id = None
        is_forward = False
        label = ''
        write_to = ''
        
        try:
            write_to = request.args.get('write_to')
        except:
            pass

        try:
            message_id = int(request.args.get('message_id'))
            is_forward = int(request.args.get('forward')) == 1
            label = request.args.get('label')
        except:
            pass

        # retrieve users list
        recipients_list = UserManager.get_users_list(current_user.id)

        # TODO CHECKS SU STA GET

        recipient_emails = [(user.email, user.email) for user in recipients_list]
        
        form.recipients.choices = recipient_emails

        single_recipient = ''
        new_message_content = ''

        # if the message is a forward message, get the original one
        if is_forward and message_id is not None and label in ['received', 'delivered']:
            
            message, status_code = MessageManager.get_message_details(current_user.id, message_id, label)

            # redirect the user to /messages without content
            if status_code != 200:
                form.content.errors.append("An error occours during message retrievement")
                
                return render_template('new_message.html', form = form, single_recipient = single_recipient)

            if label == 'delivered':
                recipients_list = ""
                message : PendingDeliveredMessage
                user : Recipient

                for user in message.recipients:
                    recipients_list = recipients_list + "%s %s (%s)\n", (user.firstname, user.lastname, user.email)
                
                new_message_content = "Sent by me to\n" + recipients_list + "\n\n" + message.content + "\"\n"
            
            else:
                # label = 'received'
                message : ReceivedMessage

                new_message_content = "Received by me from %s %s (%s)\n", (message.sender_firstname, message.sender_lastname, message.sender_email)\
                     + "\n\n" + message.content + "\"\n"

        # if it is a reply message, set the sender as the unique recipient
        elif write_to != '':
            single_recipient = write_to
        
        form.content.data = new_message_content
        
        return render_template('new_message.html', form = form, single_recipient = single_recipient)

    elif request.method == 'POST':

        form = request.form

        # if no recipients have been selected
        if len(form.getlist('recipients')) == 0: 
            flash("Please select at least 1 recipient")
            return redirect('/messages')
        
        #date validation
        deliver_time = datetime.datetime.strptime(form['deliver_time'], '%Y-%m-%dT%H:%M')
        print(deliver_time)
        deliver_time = MessageManager.validate_datetime(deliver_time)

        # verify that an image has been inserted
        imageb64    = ""
        file_name   = ""
        if request.files and request.files['attach_image'].filename != '': 

            # takes the image
            file        = request.files['attach_image']
            file_name   = request.files['attach_image'].filename

            #converts the given file in base64
            imageb64 = MessageManager.convert_image(file)
        
        MessageManager.send_message(
            current_user.id,
            str(deliver_time),
            form['content'],
            form.getlist('recipients'),
            (form['submit'] == 'Save draft'),
            imageb64,
            file_name
        )

        return render_template("index.html") 
          
    else:
        raise RuntimeError('This should not happen!')

@messages.route('/hide', methods=['POST'])
@login_required
def _hide_message():
    pass

@messages.route('/report', methods=['POST'])
@login_required
def _report_message():
    pass

@messages.route('/messages/<label>/<message_id>/attachment', methods=['GET'])
@login_required
def _get_attachment():
    pass

@messages.route('/messages/<label>/<message_id>/remove', methods=['GET'])
@login_required
def _delete_message():
    pass

