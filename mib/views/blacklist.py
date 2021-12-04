import base64

from flask import Blueprint, redirect, render_template, flash, abort, request
from flask_login import login_required
from flask_login import current_user, logout_user

from flask_login.utils import _get_user
from flask_wtf.form import _is_submitted
from flask.helpers import send_from_directory
import os
from mib.forms import BlockForm
from mib.forms.user import UnregisterForm, ModifyPersonalDataForm, ModifyPasswordForm, ContentFilterForm, ProfilePictureForm, BlockForm, SearchUserForm
from PIL import Image
from mib.rao.user_manager import BlacklistManager, UserManager

from io import BytesIO
users = Blueprint('blacklist', __name__)


@login_required
@users.route('/blacklist', methods=['GET'])
def _retrieve_blacklist():

    blacklist = BlacklistManager.retrieving_blacklist(
        current_user.id
    )

    users = UserManager.get_users_list(
        current_user
    )

    return render_template('blacklist.html', blacklist = blacklist, users = users)
 



@login_required
@users.route('/block', methods=['POST'])
def _block_user():
    form = BlockForm()

    if not form.validate_on_submit():
        abort(400)

    target = 0
    try:
        # retrieve the user id from 
        target = int(form.user_id.data)
    except:
        abort(400)

    # checking that we are not trying to block ourselves
    if current_user.id == target:
        abort(400)  # bad request

    response = BlacklistManager.block(
        current_user.id,
        target

    )
    if response.status_code == 201:
        return redirect('/blacklist')

    else:
        abort(500,'Failure in adding the user to blacklist')
