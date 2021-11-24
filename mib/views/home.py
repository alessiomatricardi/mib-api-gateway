from flask import Blueprint, render_template

home = Blueprint('home', __name__)


@home.route('/', methods=['GET'])
def _index():
    # render the homepage
    return render_template("index.html")

