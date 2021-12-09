import wtforms as f
from flask_wtf import FlaskForm
from wtforms.validators import DataRequired
from flask_wtf.file import FileAllowed, FileField

MESSAGE_IMAGE_ALLOWED_FORMATS = ['png', 'jpg', 'jpeg', 'gif', 'PNG', 'JPG', 'JPEG', 'GIF']
format_message = "Image allowed formats are PNG, JPEG and GIF"


class MultiCheckboxField(f.SelectMultipleField):
    '''
    Class which define a multi-checkbox field in order to select multiple recipients
    '''
    widget = f.widgets.ListWidget(
        prefix_label=False
    )

    option_widget = f.widgets.CheckboxInput()

class MessageForm(FlaskForm):
    """
    Form created to allow users write a message.
    This form requires a content, a delivery time and at least 1 recipient.
    """

    recipients = MultiCheckboxField(
        'Recipients', 
        choices=[]
    ) # TODO write javascript script that set/remove the required attribute from the checkist
    
    content = f.TextAreaField(
        'Content', 
        validators=[DataRequired()]
    )
    
    deliver_time = f.DateTimeField(
        'Delivery time', 
        validators=[DataRequired()], 
        render_kw={'type': 'datetime-local'}
    )
    
    attach_image = FileField(
        validators=[FileAllowed(MESSAGE_IMAGE_ALLOWED_FORMATS, format_message)]
    )

class DraftForm(MessageForm):
    '''
    Form which allow users to modify their draft messages
    '''
    delete_image = f.BooleanField()

class ReportForm(FlaskForm):
    '''
    Form which allows users to report a message
    '''
    message_id = f.HiddenField(validators=[DataRequired()])


class HideForm(FlaskForm):
    '''
    Form which allows users to hide a message
    '''
    message_id = f.HiddenField(validators=[DataRequired()])