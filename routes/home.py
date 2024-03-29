from flask import render_template, Blueprint

homeBlueprint = Blueprint("home", __name__)

@homeBlueprint.route("/")
def home():
    return render_template("home.html")

@homeBlueprint.app_errorhandler(404)
def handleInvalidRoute(err):
    print(err)
    return render_template("error.html", error=err)