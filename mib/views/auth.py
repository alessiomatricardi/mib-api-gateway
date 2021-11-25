from flask import Blueprint, flash, redirect, render_template, url_for, request
from flask_login import login_required, login_user, logout_user
from mib.forms import LoginForm
from mib.rao.user_manager import UserManager
from flask_login import current_user

auth = Blueprint('auth', __name__)


@auth.route('/login', methods=['GET', 'POST'])
def _login():
    # if the user is already logged in, redirect him to homepage
    if current_user is not None and hasattr(current_user, 'id'):
        return redirect('/')
    
    form = LoginForm()

    if request.method == 'POST':

        if form.validate_on_submit():
            email, password = form.data['email'], form.data['password']
            user = UserManager.login_user(email, password)

            # the user doesn't exists
            if user is None:
                # this add an error message that will be printed on screen
                form.email.errors.append(
                    "Account " + email + " does not exist."
                )
                return render_template('login.html', form=form)
            
            # login the user
            login_user(user)
            return redirect('/')

            # TODO handle when the user is no more active
            
            authenticated = user.authenticate(password)

            if user.is_active and authenticated:
                # login the user
                login_user(user)
                return redirect('/')
            elif not user.is_active:
                # the user unregistered his profile
                # this add an error message that will be printed on screen
                form.email.errors.append(
                    "This account is no longer active."
                )
            else:
                # wrong password
                # this add an error message that will be printed on screen
                form.password.errors.append(
                    "Password is wrong."
                )
    
        return render_template('login.html', form=form)
    else:
        return render_template('login.html', form=form)

'''
TODO work on @login_required or on a similar macro to avoid the code below in every function
if current_user is not None and hasattr(current_user, 'id'):
    // do something

instead, we can revert the logic with something like @login_required
if not current_user.is_authenticated:
    // you can't perform this action - unauthorized

or, in opposite to the first guard in this comment
if current_user is None or not hasattr(current_user, 'id'):
    // you can't perform this action - unauthorized

or, a merge of this 2 methods:

if current_user is None or not current_user.is_authenticated:
    // you can't perform this action - unauthorized
'''
@auth.route("/logout", methods=['GET'])
#@login_required
def _logout():
    # if the user is not logged in, don't logout and directly redirect him to homepage
    if current_user is not None and hasattr(current_user, 'id'):
        logout_user()
    
    return redirect('/')
