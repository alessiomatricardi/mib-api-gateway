import wtforms as f
from flask_wtf import FlaskForm
from wtforms.fields.html5 import DateField, EmailField
from wtforms.validators import DataRequired, Email, Length

from mib.validators.age import AgeValidator

class UserForm(FlaskForm):
    """Form created to allow the customers sign up to the application.
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
        validators=[AgeValidator(min_age=18)],
        render_kw = {'type' : 'date'}
    )

    display = ['email', 'firstname', 'lastname', 'date_of_birth', 'password']
