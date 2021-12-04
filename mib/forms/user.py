import wtforms as f
from flask_wtf import FlaskForm
from wtforms.fields.html5 import DateField, EmailField
from wtforms.validators import DataRequired, Email, Length
from flask_wtf.file import FileRequired, FileField

from mib.validators.age import AgeValidator

class UserForm(FlaskForm):
    """
    Form created to allow users sign up to the application.
    This form requires all the personal information, in order to create the account.
    """

    email = EmailField(
        'E-mail',
        validators=[DataRequired(), Email()]
    )

    firstname = f.StringField(
        'First name',
        validators=[DataRequired()]
    )

    lastname = f.StringField(
        'Last name',
        validators=[DataRequired()]
    )

    password = f.PasswordField(
        'Password',
        validators=[
            DataRequired(),
            # this allow us to check the password on server-side
            Length(min = 8, message = 'Password must be at least %(min)d characters'),
        ],
        # this add minlength attribute to the <input> rendered, for client-side check
        render_kw = {'minlength' : '8'}
    )

    date_of_birth = DateField(
        'Date of birth',
        validators=[DataRequired(), AgeValidator(min_age=18)],
        render_kw = {'type' : 'date'}
    )

    display = ['email', 'firstname', 'lastname', 'date_of_birth', 'password']

class UnregisterForm(FlaskForm):
    """
    Form created to allow users unregister from the application.
    This form requires the password of the user.
    """

    password = f.PasswordField(
        'Password',
        validators=[
            DataRequired(),
            # this allow us to check the password on server-side
            Length(min = 8, message = 'Password must be at least %(min)d characters'),
        ],
        # this add minlength attribute to the <input> rendered, for client-side check
        render_kw = {'minlength' : '8'}
    )
    
    display = ['password']

class ModifyPictureForm(FlaskForm):
    """
    Form created to allow users modify his profile picture.
    This form requires an image.
    """

    image = FileField(
        validators=[FileRequired('File cannot be empty!')]
    )

class SearchUserForm(FlaskForm):
    """
    Form created to allow users search other users.
    """

    firstname = f.StringField(
        'First name'
    )

    lastname = f.StringField(
        'Last name'
    )

    email = f.StringField(
        'E-mail'
    )

    display = ['firstname', 'lastname', 'email']
    
class ModifyPersonalDataForm(FlaskForm):
    """
    Form created to allow users modify his personal data.
    This form requires all data.
    """

    firstname = f.StringField(
        'First name', 
        validators=[DataRequired()]
    )

    lastname = f.StringField(
        'Last name', 
        validators=[DataRequired()]
    )

    date_of_birth = DateField(
        'Date of birth',
        validators=[DataRequired(), AgeValidator(min_age=18)],
        render_kw = {'type' : 'date'}
    )

    display = ['firstname', 'lastname', 'date_of_birth']

class ModifyPasswordForm(FlaskForm):
    """
    Form created to allow users modify his password.
    This form requires all data.
    """

    old_password = f.PasswordField(
        'Old password', 
        validators=[
            DataRequired(),
            # this allow us to check the password on server-side
            Length(min = 8, message = 'Password must be at least %(min)d characters'),
        ],
        # this add minlength attribute to the <input> rendered, for client-side check
        render_kw = {'minlength' : '8'}
    )
    
    new_password = f.PasswordField(
        'New password', 
        validators=[
            DataRequired(),
            # this allow us to check the password on server-side
            Length(min = 8, message = 'Password must be at least %(min)d characters'),
        ],
        # this add minlength attribute to the <input> rendered, for client-side check
        render_kw = {'minlength' : '8'}
    )

    repeat_new_password = f.PasswordField(
        'Repeat the new password', 
        validators=[
            DataRequired(),
            # this allow us to check the password on server-side
            Length(min = 8, message = 'Password must be at least %(min)d characters'),
        ],
        # this add minlength attribute to the <input> rendered, for client-side check
        render_kw = {'minlength' : '8'}
    )
    
    display = ['old_password', 'new_password', 'repeat_new_password']

class ContentFilterForm(FlaskForm):
    '''
    TODO COMMENTARE
    '''
    filter_enabled = f.BooleanField()

class ProfilePictureForm(FlaskForm):
    image = FileField(validators=[FileRequired('File was empty!')])

class BlockForm(FlaskForm):
    user_id = f.HiddenField(validators=[DataRequired()])
