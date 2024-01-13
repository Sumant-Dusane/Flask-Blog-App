from flask import Blueprint, render_template

authBlueprint = Blueprint("login", __name__)

@authBlueprint.route("/login")
def loginUser():
    try:
        return render_template("auth/auth.html", type="login")
    except Exception as err:
        print("Error in /login: ", err)
        return render_template("error.html")

@authBlueprint.route("/signup")
def registerUser():
    try:
        return render_template("auth/auth.html", type="signup")
    except Exception as err:
        print("Error in /signup: ", err)
        return render_template("error.html")