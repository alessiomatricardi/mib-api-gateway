from .auth import auth
from .home import home
from .users import users
from .blacklist import blacklist
"""List of the views to be visible through the project
"""
blueprints = [home, auth, users, blacklist]
