from flask import Blueprint, render_template, abort, request, flash
from flask_login import current_user
from flask_login.utils import login_required
from werkzeug.utils import redirect, secure_filename
from mib.rao.messages_manager import MessageManager
from mib.rao.user_manager import UserManager
from mib.forms.message import HideForm, ReportForm, DraftForm
from mib.rao.messages import ReceivedMessage, DraftMessage, PendingDeliveredMessage
from typing import List
import datetime

bottlebox = Blueprint('bottlebox', __name__)


@bottlebox.route('/bottlebox', methods=['GET'])
@login_required
def _bottlebox_home():
    # render the homepage
    return render_template("bottlebox_home.html")

@bottlebox.route('/bottlebox/received', methods=['GET'])
@login_required
def _show_received():

    messages, status_code = MessageManager.get_bottlebox(current_user.id, 'received')

    if status_code != 200:
        abort(status_code)
    
    return render_template("bottlebox.html", messages = messages, label = 'Received')

@bottlebox.route('/bottlebox/drafts', methods=['GET'])
@login_required
def _show_drafts():

    messages, status_code = MessageManager.get_bottlebox(current_user.id, 'drafts')

    if status_code != 200:
        abort(status_code)
    
    return render_template("bottlebox.html", messages = messages, label = 'Drafts')

@bottlebox.route('/bottlebox/pending', methods=['GET'])
@login_required
def _show_pending():

    messages, status_code = MessageManager.get_bottlebox(current_user.id, 'pending')

    if status_code != 200:
        abort(status_code)
    
    return render_template("bottlebox.html", messages = messages, label = 'Pending')

@bottlebox.route('/bottlebox/delivered', methods=['GET'])
@login_required
def _show_delivered():

    messages, status_code = MessageManager.get_bottlebox(current_user.id, 'delivered')

    if status_code != 200:
        abort(status_code)
    
    return render_template("bottlebox.html", messages = messages, label = 'Delivered')

@bottlebox.route('/messages/received/<message_id>', methods=['GET'])
@login_required
def _show_received_message(message_id):
    
    # checks if <message_id> is a number, otherwise abort
    try:
        message_id = int(message_id)
    except:
        abort(404)

    message : ReceivedMessage
    message, status_code = MessageManager.get_message_details(current_user.id, message_id, 'received')

    if status_code != 200:
        abort(status_code)
    
    # create utils form for actions
    hideForm = HideForm(message_id = message.id)
    reportForm = ReportForm(message_id = message.id)
    
    return render_template("message_detail.html", message = message, label = 'received', hideForm = hideForm, reportForm = reportForm)

@bottlebox.route('/messages/drafts/<message_id>', methods=['GET', 'POST'])
@login_required
def _show_draft_message(message_id):
    
    # checks if <message_id> is a number, otherwise abort
    try:
        message_id = int(message_id)
    except:
        abort(404)

    form = DraftForm()

    message : DraftMessage
    message, status_code = MessageManager.get_message_details(current_user.id, message_id, 'drafts')

    if status_code != 200:
        abort(status_code)

    # defining format of datetime in order to insert it in html form
    deliver_time = message.deliver_time.strftime("%Y-%m-%dT%H:%M")

    if status_code != 200:
        abort(status_code)
    
    # rendering the draft detail
    if request.method == 'GET':
        
        form.content.data = message.content

        # retrieve users
        users, status_code = UserManager.get_users_list(current_user.id)

        if status_code != 200:
            abort(status_code)

        form.recipients.choices = [(user.email, user.email) for user in users]

        form.delete_image.data = False

        # returning the draft html page
        return render_template("modify_draft.html", form = form, deliver_time = deliver_time, message = message, recipients_emails = message.recipients)
    
    elif request.method == 'POST':
        
        if not form.attach_image.validate(form):
            
            # retrieve users list
            recipients_list, status_code = UserManager.get_users_list(current_user.id)

            if status_code != 200:
                abort(status_code)

            recipient_emails = [(user.email, user.email) for user in recipients_list]
            
            form.recipients.choices = recipient_emails

            form.delete_image.data = False

            # returning the draft html page
            return render_template("modify_draft.html", form = form, deliver_time = deliver_time, message = message, recipients_emails = message.recipients)
        
        form = request.form

        # if no recipients have been selected
        if len(form.getlist('recipients')) == 0: 

            flash("Please select at least 1 recipient")

            redirect_to = '/messages/drafts/%s' % message_id

            return redirect(redirect_to)

        # delete draft from db, eventual image in filesystem and all message_recipients instances
        if form['submit'] == 'Delete draft':

            msg, status_code = MessageManager.delete_message(current_user.id, 'drafts', message_id)

            if status_code != 200:
                abort(status_code)
            
            return redirect('/bottlebox/drafts')
        
        draft_json = dict()

        draft_json['requester_id'] = current_user.id
        draft_json['content'] = form['content']
        draft_json['delete_image'] = form.get('delete_image') == 'y' or False

        # date validation
        deliver_time = form['deliver_time']
        deliver_time = datetime.datetime.strptime(deliver_time, '%Y-%m-%dT%H:%M')
        deliver_time = MessageManager.validate_datetime(deliver_time)
        draft_json['deliver_time'] = str(deliver_time)
        
        draft_json['is_sent'] = False
        draft_json['recipients'] = []
        draft_json['image'] = ''
        draft_json['image_filename'] = ''
        
        # checking if there is a new attached image in the form
        if request.files and request.files['attach_image'].filename != '':

            # retrieving newly attached image
            file = request.files['attach_image']

            # image should be passed as base64 string
            draft_json['image'] = MessageManager.convert_image(file)

            draft_json['image_filename'] = secure_filename(file.filename)

        if form['submit'] == 'Send bottle':
            draft_json['is_sent'] = True
        
        recipient_emails = list()

        # checking if there's new recipients for the draft
        for recipient in form.getlist('recipients'):

            recipient_emails.append(recipient)
        
        draft_json['recipients'] = recipient_emails

        status_code = MessageManager.modify_draft(message_id, draft_json)

        if status_code != 200:
            abort(status_code)

        if form['submit'] == 'Send bottle':
            redirect_to = '/messages/pending/%s' % message.id
            return redirect(redirect_to)
        else:
            return redirect('/bottlebox/drafts')

@bottlebox.route('/messages/delivered/<message_id>', methods=['GET'])
@login_required
def _show_delivered_message(message_id):
    
    # checks if <message_id> is a number, otherwise abort
    try:
        message_id = int(message_id)
    except:
        abort(404)
    
    message : PendingDeliveredMessage
    message, status_code = MessageManager.get_message_details(current_user.id, message_id, 'delivered')

    if status_code != 200:
        abort(status_code)
    
    return render_template("message_detail.html", message = message, label = 'delivered')

@bottlebox.route('/messages/pending/<message_id>', methods=['GET'])
@login_required
def _show_pending_message(message_id):
    
    # checks if <message_id> is a number, otherwise abort
    try:
        message_id = int(message_id)
    except:
        abort(404)
    
    message : PendingDeliveredMessage
    message, status_code = MessageManager.get_message_details(current_user.id, message_id, 'pending')

    if status_code != 200:
        abort(status_code)
    
    return render_template("message_detail.html", message = message, label = 'pending')