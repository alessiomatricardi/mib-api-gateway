import datetime
from flask import Blueprint, redirect, render_template, flash, request, abort
from flask_login import login_required, current_user
from mib.forms.message import MessageForm, ReportForm, HideForm
from mib.rao.user_manager import UserManager
from mib.rao.messages_manager import MessageManager
from mib.rao.messages import PendingDeliveredMessage, ReceivedMessage, Recipient
from werkzeug.utils import secure_filename
import base64
from io import BytesIO
from flask.helpers import send_file

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
        recipients_list, status_code = UserManager.get_users_list(current_user.id)

        if status_code != 200:
            abort(status_code)

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
                    recipients_list = recipients_list + "%s %s (%s)\n" % (user.firstname, user.lastname, user.email)
                
                new_message_content = "Sent by me to\n" + recipients_list + "\n\n" + message.content
            
            else:
                # label = 'received'
                message : ReceivedMessage

                new_message_content = "Received from %s %s (%s)\n" % (message.sender_firstname, message.sender_lastname, message.sender_email)\
                     + "\n\n" + message.content

        # if it is a reply message, set the sender as the unique recipient
        elif write_to != '':
            single_recipient = write_to
        
        form.content.data = new_message_content
        
        return render_template('new_message.html', form = form, single_recipient = single_recipient)

    elif request.method == 'POST':

        if not form.attach_image.validate(form):
            
            # retrieve users list
            recipients_list, status_code = UserManager.get_users_list(current_user.id)

            if status_code != 200:
                abort(status_code)

            recipient_emails = [(user.email, user.email) for user in recipients_list]
            
            form.recipients.choices = recipient_emails

            return render_template('new_message.html', form = form, single_recipient = '')
        
        form = request.form

        # if no recipients have been selected
        if len(form.getlist('recipients')) == 0: 
            flash("Please select at least 1 recipient")
            return redirect('/messages')
        
        #date validation
        deliver_time = datetime.datetime.strptime(form['deliver_time'], '%Y-%m-%dT%H:%M')
        deliver_time = MessageManager.validate_datetime(deliver_time)

        # verify that an image has been inserted
        imageb64    = ""
        file_name   = ""
        if request.files and request.files['attach_image'].filename != '': 

            # takes the image
            file = request.files['attach_image']
            file_name = secure_filename(request.files['attach_image'].filename)

            #converts the given file in base64
            imageb64 = MessageManager.convert_image(file)
        
        status_code = MessageManager.send_message(
            current_user.id,
            str(deliver_time),
            form['content'],
            form.getlist('recipients'),
            (form['submit'] == 'Save draft'),
            imageb64,
            file_name
        )

        if status_code != 201:
            abort(status_code)

        return render_template("index.html") 
          
    else:
        raise RuntimeError('This should not happen!')

@messages.route('/hide', methods=['POST'])
@login_required
def _hide_message():
    
    form = HideForm()

    if not form.validate_on_submit():
        return redirect('/')

    message_id = form.message_id.data

    try:
        message_id = int(message_id)
    except:
        abort(404)
    
    status_code = MessageManager.hide_message(current_user.id, message_id)

    if status_code != 200:
        abort(status_code)
    
    return redirect('/bottlebox/received')

@messages.route('/report', methods=['POST'])
@login_required
def _report_message():

    form = ReportForm()

    if not form.validate_on_submit():
        return redirect('/')

    message_id = form.message_id.data

    try:
        message_id = int(message_id)
    except:
        abort(404)
    
    status_code = MessageManager.report_message(current_user.id, message_id)

    if status_code != 200:
        abort(status_code)
    
    return redirect('/messages/received/%s' % str(message_id))

@messages.route('/messages/<label>/<message_id>/attachment', methods=['GET'])
@login_required
def _get_attachment(label, message_id):
    
    try:
        message_id = int(message_id)
    except:
        abort(404)
    
    image_base64, image_filename, status_code = MessageManager.get_attachment(current_user.id, label, message_id)

    if status_code != 200:
        abort(status_code)

    img_data = BytesIO(base64.b64decode(image_base64))

    format = str(image_filename).capitalize().split(".")[1]

    mimetype = 'image/jpeg'

    if format == 'PNG':
        mimetype = 'image/png'
    elif format == 'GIF':
        mimetype = 'image/gif'

    return send_file(img_data, mimetype=mimetype)

@messages.route('/messages/pending/<message_id>/remove', methods=['GET'])
@login_required
def _delete_pending_message(message_id):
    
    try:
        message_id = int(message_id)
    except:
        abort(404)
    
    message, status_code = MessageManager.delete_message(current_user.id, 'pending', message_id)

    if status_code != 200:
        if status_code == 403 and str(message).count('points') > 0:
            flash(message)
            return redirect('/messages/pending/%s' % str(message_id))
        else:
            abort(status_code)
    
    return redirect('/bottlebox/pending')

