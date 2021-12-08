import base64
import os
import requests
import datetime

from flask                      import Blueprint, redirect, render_template, flash, abort, request
from flask_login                import login_required, current_user, logout_user

from flask_login.utils          import _get_user
from flask_wtf.form             import _is_submitted
from flask.helpers              import send_from_directory

from werkzeug.utils             import secure_filename

from PIL                        import Image

from mib.forms.message          import MessageForm, MultiCheckboxField
from mib.rao.user_manager       import UserManager
from mib.rao.messages_manager   import MessageManager
from io                         import BytesIO

messages = Blueprint('messages', __name__)


@login_required
@messages.route('/messages', methods=['GET', 'POST'])
def new_message():
    """
    This method allows to create and handle a new message
    """

    if request.method == 'GET':
        """
        body get
        {
            'forward'   : bool,
            'draft'     : bool,
            'reply'     : bool,
            'write_to'  : string, #i want to put here an email
            'label'     : string,
            'message_id': int
         }
        """
        data = request.get_json() # request's body
        form = MessageForm() # new blank form

        recipients_list         = UserManager._get_users_list(current_user.id)
        form.recipients.choices = recipients_list

        message_id      = int(request.args.get('message_id'))
        is_forward      = int(request.args.get('forward'))
        is_draft        = int(request.args.get('draft'))
        is_reply        = int(request.args.get('reply'))
        label           = request.args.get('label')
        write_to        = request.args.get('write_to')

        
        single_recipient    = ''
        message_json        = {}

        if is_forward or is_draft or is_reply:
            # message request
            message_json = MessageManager.get_message_details(current_user.id, message_id, label)
            if message_json is None:
                abort(404) #TODO fai robe

        if is_forward:
            
            if label == 'delivered':
                """
                is returned 
                {
                    'content' : string,
                    'recipients' : 
                        {
                            'email'                 : string, 
                            'id'                    : int,
                            'firstname,lastname'    : string,
                            'is_in_blacklist'       : bool
                        }
                }
                """

                recipients_list = ""

                for user in message_json['recipients']:
                    recipients_list = recipients_list + user['firstname'] + " " + user['firstname'] + "\n"
                
                new_message_content = "Sent by me\nto " + recipients_list + "\"" + message_json['content'] + "\"\n" 
                
            if label == 'received': 
                """
                is returned
                {
                    'sender_firstname'          : string,
                    'sender_lastname'           : string,
                    'sender_email'              : string,
                    'is_sender_in_blacklist'    : bool,
                    'is_read'                   : int,
                    'content'                   : string,
                    'is_reported'               : int
                }
                """
                new_message_content = "Received by me from " + message_json['sender_firstname'] + " " + message_json['sender_lastname'] + ":\n\"" + message_json['content'] + "\""           


            form.recipients.check()  


        if is_draft:
            """
            is returned
            {
                'id'            : int,
                'sender_id'     : int, 
                'content',      : int,
                'deliver_time'  : datetime, 
                'image'         : int,
                'recipients'    : email list
            }
            """
            form.content        = message_json['content']
            form.deliver_time   = message_json['deliver_time']
            
            single_recipient    = message_json['recipients'][0] # TODO single recipients
                                                                # deve essere una lista in modo che 
                                                                # nel template 
                                                                # vengano spuntate tutte le mail 
                                                                # presenti in questa lista

        if is_reply:
            """
            is returned
            {
                'sender_firstname'          : string,
                'sender_lastname'           : string,
                'sender_email'              : string,
                'is_sender_in_blacklist'    : bool,
                'is_read'                   : int,
                'content'                   : string,
                'is_reported'               : int
            }
            """
            single_recipient = message_json['sender_email'][0]
        
        if write_to:
            single_recipient = write_to


        # passing list of recipients to the form
        email_list = []
        for user in UserManager._get_users_list(current_user.id):
            email_list.append((user.email,user.email))
        form.recipients.choices = email_list
        #####
        
        return render_template('new_message.html', form=form, single_recipient=single_recipient)

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

            # checks on the given file
            if MessageManager.validate_file(file): 

                #converts the given file in base64
                imageb64 = MessageManager.convert_image(file)

            else:
                flash('Insert an image with extention: .png , .jpg, .jpeg, .gif')
                return redirect('/messages')
        
        
        MessageManager.send_message(current_user.id, str(deliver_time), form['content'], form.getlist('recipients'), (form['submit'] == 'Save draft'), imageb64, file_name)

        return render_template("index.html") 
          
    else:
        raise RuntimeError('This should not happen!')



