from .auth import auth
from .home import home
from .users import users
from .messages import messages
from .blacklist import blacklist
from .bottlebox import bottlebox

"""List of the views to be visible through the project
"""
blueprints = [home, auth, users, messages, bottlebox, blacklist]
