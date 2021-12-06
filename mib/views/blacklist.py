from flask import Blueprint, redirect, render_template, abort
from flask_login import login_required
from flask_login import current_user
from mib.forms.user import BlockForm, UnblockForm

from mib.rao.user_manager import UserManager
from mib.rao.blacklist_manager import BlacklistManager


blacklist = Blueprint('blacklist', __name__)



@login_required
@blacklist.route('/blacklist', methods=['GET'])
def _retrieve_blacklist():

    #TODO check error cases
    requester_id = current_user.id
    
    #retrieves the ids of all the users blocked by the requester
    blocked_ids = BlacklistManager.retrieving_blacklist(
        requester_id
    )

    blacklist = []
    
    #retrieve the user associated to each id in blocked_ids list
    for i in blocked_ids:
        user = UserManager.get_user_by_id(
            i,
            i
        )
        blacklist.append(user)


    return render_template('blacklist.html', blacklist = blacklist)
 



@login_required
@blacklist.route('/block', methods=['POST'])
def _block_user():
    form = BlockForm()

    if not form.validate_on_submit():
        abort(400)

    target = 0
    try:
        # retrieve the user id from the form
        target = int(form.user_id.data)
    except:
        abort(400)

    # checking that we are not trying to block ourselves
    if current_user.id == target:
        abort(400)  # bad request

    response = BlacklistManager.block(
        target,
        current_user.id,
    )

    #if the target has been succesfully blocked
    if response.status_code == 201:
        return redirect('/blacklist')

    else:
        abort(500,'Failure in adding the user to blacklist')


@login_required
@blacklist.route('/unblock', methods=['POST'])
def _unblock_user():


    form = UnblockForm()

    if not form.validate_on_submit():
        abort(400)

    target = 0
    try:
        # retrieve the user id from the form
        target = int(form.user_id.data)
    except:
        abort(400)

    # checking that we are not trying to unblock ourselves
    if current_user.id == target:
        abort(400) # bad request

    response = BlacklistManager.unblock(
        target,
        current_user.id
    )
   
    #target successfully deleted from the requester's blacklist
    if response.status_code == 202:
        return redirect('/blacklist')
    elif response.status_code == 404:
        abort(404, 'You are trying to block a non existing user!')
    else:
        abort(500)


