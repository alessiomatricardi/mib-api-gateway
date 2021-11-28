import wtforms as f
from flask_wtf import FlaskForm
from wtforms.validators import DataRequired,Email, Length
from wtforms import widgets, SelectMultipleField
from wtforms.fields.html5 import EmailField
from flask_wtf.file import FileAllowed, FileRequired, FileField


# TODO WITH AJAX THESE FORMS SHOULD BE USELESS
class ReportForm(FlaskForm):
    message_id = f.HiddenField(validators=[DataRequired()])


class HideForm(FlaskForm):
    message_id = f.HiddenField(validators=[DataRequired()])


class BlockForm(FlaskForm):
    user_id = f.HiddenField(validators=[DataRequired()])


class UnblockForm(FlaskForm):
    user_id = f.HiddenField(validators=[DataRequired()])


class ContentFilterForm(FlaskForm):
    filter_enabled = f.BooleanField()