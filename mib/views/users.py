import base64

from flask import Blueprint, redirect, render_template, flash, abort, request
from flask_login import login_required
from flask_login import current_user, logout_user

from flask_login.utils import _get_user
from flask_wtf.form import _is_submitted
from flask.helpers import send_from_directory
import os
from mib.forms import UserForm
from mib.forms.user import UnregisterForm, ModifyPersonalDataForm, ModifyPasswordForm, ContentFilterForm, ProfilePictureForm, BlockForm, SearchUserForm
from PIL import Image
from mib.rao.user_manager import UserManager

from io import BytesIO
users = Blueprint('users', __name__)


@users.route('/register/', methods=['GET', 'POST'])
def register():
    """This method allows the creation of a new user into the database


    Returns:
        Redirects the user into homepage, once he's logged in
    """

    # if the user is already logged in, redirect him to homepage
    #TODO usare @login_required per controllare se un utente è loggato
    if current_user is not None and hasattr(current_user, 'id'):
        return redirect('/')

    form = UserForm()

    #if the method is POST the data contained in the UserForm are sent to the UserManager.register method

    if form.is_submitted():
        email = form.data['email']
        password = form.data['password']
        firstname = form.data['firstname']
        lastname = form.data['lastname']
        date_of_birth = form.data['date_of_birth']
        date = date_of_birth.strftime('%Y-%m-%d')
        
        #the register method will send the request to the microservice User 
        response = UserManager.register(
            email,
            password,
            firstname,
            lastname,
            date,
        )

        if response.status_code == 201:
            # in this case the request is ok!
            return redirect('/')

        elif response.status_code == 200:
            # user already exists
            flash('Mail already used!')
            #TODO controllare perchè non funge
            #form.email.errors.append(email + " is not available, please register with another email.")
            return render_template('register.html', form=form)
        else:
            flash('Unexpected response from users microservice!')
            return render_template('register.html', form=form)
    else:
        for fieldName, errorMessages in form.errors.items():
            for errorMessage in errorMessages:
                flash('The field %s is incorrect: %s' % (fieldName, errorMessage))


    return render_template('register.html', form=form)


@users.route('/unregister', methods=['GET', 'POST'])
@login_required #TODO otherwise redirect to login, how?
def _unregister():
    """
    Set an account as unregistered.


    Returns:
        If the operation is successfull returns the view to the home page
    """

    form = UnregisterForm()

    if request.method == 'POST':

        if form.validate_on_submit():

            password = form.data['password']

            response = UserManager.unregister(current_user.id, password)

            #TODO add flash messages ???
            if response.status_code == 404:
                # if the user is not found, then logout it directly
                redirect('/logout')

            elif response.status_code == 401:
                # Password is wrong, so user is unauthorized

                return render_template('unregister.html', form=form, user=current_user)

            else:
                #the user successfully unregistered
                logout_user()
                return redirect('/')

    return render_template('unregister.html', form=form, user=current_user)


@login_required
@users.route('/profile/data/edit', methods=['GET', 'POST'])
def _modify_personal_data():
    """
    Modify firstname lastname and date of birth of the user.


    Returns:
        If the operation is successfull returns the view of the profile updated
    """
    form = ModifyPersonalDataForm()

    if request.method == 'POST':

        if form.validate_on_submit():

            id = current_user.id
            firstname = form.data['firstname']
            lastname = form.data['lastname']
            date_of_birth = form.data['date_of_birth']
            birthdate = date_of_birth.strftime("%Y-%m-%d")

            response = UserManager.modify_data(id, firstname, lastname,
                                               birthdate)

            # if user data are correctly modified
            if response.status_code == 200:
                return redirect('/profile')

            # something went wrong
            # TODO si può stampare qualcosa?

            return render_template('modify_personal_data.html', form=form)

    elif request.method == 'GET':
        # populate the form with the existing data of the user
        form.firstname.data = current_user.firstname
        form.lastname.data = current_user.lastname
        form.date_of_birth.data = current_user.date_of_birth

    return render_template('modify_personal_data.html', form=form)

@login_required # TODO SERVE????
@users.route('/profile/password/edit', methods=['GET', 'POST'])
def _modify_password():
    """
    Set a new password for the user.


    Returns:
        If the operation is successfull returns the view of the profile.
    """
    form = ModifyPasswordForm()

    if request.method == 'POST':

        if form.validate_on_submit():

            id = current_user.id
            old_password = form.data['old_password']
            new_password = form.data['new_password']
            repeat_new_password = form.data['repeat_new_password']

            response = UserManager.modify_password(
                id,
                old_password,
                new_password,
                repeat_new_password
            )

            # user inserted a wrong password
            if response.status_code == 401:
                form.old_password.errors.append(
                    "The old password you inserted is incorrect. Please insert the correct one."
                )

            # new password is equal to the old or new and repeated aren't equal
            elif response.status_code == 400:
                message_to_print = "TODO TODO TODO" # TODO retrieve from response
                form.new_password.errors.append(
                    message_to_print)

            #TODO check if it is necessary after @login_required fix
            elif response.status_code == 404:
                return redirect('/logout')

            else:
                # something went wrong???
                return redirect('/profile')


    return render_template('modify_password.html', form=form)

@users.route('/profile', methods=['GET'])
def _show_profile():
    """
    Show the profile of the user.
    """
    if current_user is not None and hasattr(current_user, 'id'):

        content_filter_form = ContentFilterForm(
            filter_enabled=current_user.content_filter_enabled)

        # show user informations
        return render_template("user_details.html",
                               user=current_user,
                               content_filter_form = content_filter_form
                               )
    else:
        return redirect("/login")

@login_required
@users.route('/profile/content_filter', methods=['POST'])
def _content_filter():
    """
    enable/disable the content filter of the user.


    Returns:
        If the operation is successfull shows the view of the profile updated.
    """
    form = ContentFilterForm()

    if form.validate_on_submit():

        id = current_user.id
        enabled = form.data['filter_enabled']

        response = UserManager.modify_content_filter(id, enabled)

        if response.status_code == 404:
            return redirect('/logout')

        else:
            # TODO SHOW SOMETHING?
            return redirect('/profile')
    else:

        return redirect('/profile')


@login_required
@users.route('/profile/picture/edit', methods=['GET','POST'])
def _modify_profile_picture():
    """
    Set a new profile picture for the user.


    Returns:
        If the operation is successfull returns the view of the profile.
    """
    form = ProfilePictureForm()

    if request.method == 'POST':

        if form.validate_on_submit(): # TODO VALIDATE IMAGES
            data = form.data['image']

            img = data.stream.read()
            str_image = base64.encodebytes(img).decode('utf-8')

            id = current_user.id
            
            response = UserManager.modify_profile_picture(
                id,
                str_image
            )

            if response.status_code == 404:

                return redirect('/logout')
            elif response.status_code == 500:

                abort(500)
                #TODO possiamo gestirlo meglio? magari dicendo qualcosa all'utente
            else:

                return redirect('/profile')

    return render_template('modify_picture.html', form=form)

@login_required
@users.route('/users', methods=['GET'])
def _users():
    # checking if there is a logged user, otherwise redirect to login
    requester_id = current_user.id


    recipients = UserManager._get_users_list(
        requester_id
    )
        # rendering the template
        # update result whit template
    return render_template("users.html", users=recipients)

@login_required
@users.route('/users/<user_id>', methods=['GET'])
def _get_user(user_id):
   
    requester_id = current_user.id

    if requester_id == int(user_id):
        return redirect('/profile')
    
    #user = User()
    user = UserManager.get_user_by_id(
        user_id,
        requester_id
    )

    block_form = BlockForm(user_id = user.id)
    return render_template('user_details.html', user = user, block_form = block_form)


@login_required
@users.route('/users/<user_id>/picture', methods=['GET'])
def _get_profile_photo(user_id):
    
    """
    id user_id has no profile picture, the MS user will return the default image which will
    be save sa str(user_id)+"_100.jpeg"
    """

    images = UserManager._get_user_picture(
        int(user_id)
    )
    image = images['image']
        # rendering the template
        # update result whit template

    img_data = BytesIO(base64.b64decode(image))
    
    img = Image.open(img_data)
    img = img.convert('RGB') # in order to support also Alpha transparency images such as PNGs
    img = img.resize([256, 256], Image.ANTIALIAS)
    path_to_save = os.path.join(os.getcwd(), 'mib', 'static', 'pictures', str(user_id) + '.jpeg')
    #delete image if it already exists
    if os.path.exists(path_to_save):
        os.remove(path_to_save) 

    img.save(path_to_save, "JPEG", quality=100, subsampling=0)

    filename = str(user_id)+ '.jpeg'
  
    return send_from_directory(os.path.join(os.getcwd(), 'mib', 'static', 'pictures'), filename)

@login_required
@users.route('/users/search', methods=['GET', 'POST'])
def _search_user():
    
    form = SearchUserForm()
    
    if request.method == 'GET':
        return render_template('search_user.html', form=form)

    else:

        form = request.form
        firstname, lastname, email = form['firstname'], form['lastname'], form['email']

        # if none of the fileds have been compiled
        if not firstname and not lastname and not email:
            #TODO check if 400 is a possbile request or can be eliminated
            flash("Insert at least one field")
            return redirect('/users/search')

        else:
            # retrieving the list of users that match with the content of the form
           
            users, status_code = UserManager._search_users(
               current_user.id,
               firstname,
               lastname,
               email
            )

            if status_code == 400:
                flash("Bad request, please insert correct parameters")
                return redirect('/users/search')

            else:

                return render_template("users.html", users=users)