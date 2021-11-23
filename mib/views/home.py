from flask import Blueprint, render_template

home = Blueprint('home', __name__)


@home.route('/', methods=['GET', 'POST'])
def index():
    """General route for the index page
    """
    return render_template("index.html")

