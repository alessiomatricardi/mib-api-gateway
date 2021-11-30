import base64

from flask import Blueprint, redirect, render_template, url_for, flash, abort, request
from flask_login import (login_user, login_required)
from flask_login import current_user, logout_user
from flask_login.utils import _get_user
from flask_wtf.form import _is_submitted

from mib.forms import UserForm
from mib.forms.user import UnregisterForm, ModifyPersonalDataForm, ModifyPasswordForm, ContentFilterForm, ProfilePictureForm

from mib.rao.user_manager import UserManager
from mib.auth.user import User

users = Blueprint('users', __name__)


@users.route('/register', methods=['GET', 'POST'])
def register():
    """This method allows the creation of a new user into the database

    Returns:
        Redirects the user into his profile page, once he's logged in
    """
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
            flash('User already exists!')
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

    if form.is_submitted():
        password = form.data['password']
        id = current_user.id
        
        response = UserManager.unregister(
            id,
            password
        )
        
        if response.status_code == 404:
            redirect('/login')
        
        elif response.status_code == 401:
            #Password is wrong, so user is unauthorized
            return render_template('unregister.html', form=form, user=current_user)

        else:
            #the user successfully unregistered
            logout_user()
            return redirect('/')
    else:
        return render_template('unregister.html', form=form, user=current_user)


@login_required
@users.route('/profile/data/edit', methods=['GET', 'POST'])
def _modify_personal_data():
    """
    MOdify firstname lastname and date of birth of the user.


    Returns:
        If the operation is successfull returns the view of the profile updated
    """
    form = ModifyPersonalDataForm()
    
    if form.is_submitted() :
        
        id = current_user.id
        firstname = form.data['firstname']
        lastname = form.data['lastname']
        date_of_birth = form.data['date_of_birth']
        date = date_of_birth.strftime('%Y-%m-%d')
        
        response = UserManager.modify_data(
            id,
            firstname,
            lastname,
            date
        )
    
        # if user data are correctly modified
        if response.status_code == 404:
            return redirect('/login')
        
        else:
            # if user data are correctly modified
           return redirect('/profile')

    else:
        # populate the form with the existing data of the user
        form.firstname.data = current_user.firstname
        form.lastname.data = current_user.lastname
        form.date_of_birth.data = current_user.date_of_birth

        return render_template('modify_personal_data.html', form=form)

@login_required
@users.route('/profile/password/edit', methods=['GET', 'POST'])
def _modify_password():
    """
    Set a new password for the user.


    Returns:
        If the operation is successfull returns the view of the profile.
    """
    form = ModifyPasswordForm()

    if form.is_submitted() :
        
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
    
        
        if response.status_code == 401:
            #form['old_password'].errors.append("The old password you inserted is incorrect. Please insert the correct one.")
            flash('The old password you inserted is incorrect. Please insert the correct one.')

        elif response.status_code == 403:
            #form.repeat_new_password.errors.append("The new password and its repetition must be equal.")
            flash('The new password and its repetition must be equal.')

        #TODO check if it is necessary after @login_required fix
        elif response.status_code == 404:
            return redirect('/login')
            
        elif response.status_code == 409:
            #form.new_password.errors.append("Please insert a password different from the old one.")
            flash('Please insert a password different from the old one.')
        else:
            return redirect('/profile')
            

        return render_template('modify_password.html', form=form)
    else:

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
                               content_filter_form = content_filter_form)
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
    if form.is_submitted():

        id = current_user.id
        enabled = form.data['filter_enabled']

        response = UserManager.content_filter(
            id,
            enabled
        )

        if response.status_code == 404:
            return redirect('/login')

        else:
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
    if form.is_submitted():

        data = form.data['image']
        
        img = data.stream.read()
        str_image = base64.encodebytes(img).decode('utf-8')
   
        id = current_user.id
      

        response = UserManager._modify_profile_picture(
            id,
            str_image
        )

        if response.status_code == 404:
            return redirect('/login')
        elif response.status_code == 500:
            abort(500)
        else:
            return redirect('/profile')
    else:
        return render_template('modify_picture.html', form=form)
