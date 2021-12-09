from flask import Blueprint, flash, redirect, render_template, url_for, request
from flask_login import login_required, login_user, logout_user
from mib.forms import LoginForm
from mib.rao.user_manager import UserManager
from flask_login import current_user

auth = Blueprint('auth', __name__)


@auth.route('/login', methods=['GET', 'POST'])
def _login():
    # if the user is already logged in, redirect him to homepage
    #TODO usare @login_required per controllare se un utente è loggato
    if current_user is not None and hasattr(current_user, 'id'):
        return redirect('/')
    
    form = LoginForm()

    if request.method == 'POST':

        if form.validate_on_submit():
            email, password = form.data['email'], form.data['password']
            user, status_code = UserManager.login_user(email, password)

            if user is None:
                # the user doesn't exists
                if status_code == 404:
                    # this add an error message that will be printed on screen
                    form.email.errors.append(
                        "Account " + email + " does not exist."
                    )

                elif status_code == 401:
                    form.password.errors.append(
                        "Password is wrong or this account is no longer active"
                    )
                
                return render_template('login.html', form=form)

            else:
                # login the user
                login_user(user)

                # redirect user to the desired page, if exists
                redirect_to = request.args.get('next')

                if redirect_to is None:
                    redirect_to = '/'

                return redirect(redirect_to)
        
    else:
        return render_template('login.html', form=form)


@auth.route("/logout", methods=['GET'])
@login_required
def _logout():
    
    logout_user()
    
    return redirect('/')
