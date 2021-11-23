from .auth import auth
from .home import home
from .users import users

"""List of the views to be visible through the project
"""
blueprints = [home, auth, users]
