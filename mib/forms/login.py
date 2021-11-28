import wtforms as f
from flask_wtf import FlaskForm
from wtforms.validators import DataRequired, Email
from wtforms.fields.html5 import EmailField


class LoginForm(FlaskForm):
    """
    Form created to allow users sign in to the application.
    This form requires personal email and password in order to access the account.
    """

    email = EmailField(
        'E-mail',
        validators=[DataRequired(), Email()]
    )

    password = f.PasswordField(
        'Password',
        validators=[DataRequired()]
    )

    display = ['email', 'password']
