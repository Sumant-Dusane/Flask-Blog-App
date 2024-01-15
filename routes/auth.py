from flask import Blueprint, render_template, request, session, redirect, url_for
from db.mongoDB import userCollection
import os
import re

authBlueprint = Blueprint("auth", __name__)
regex = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,7}\b'
BLOG_DATA_IMAGES = 'static/blogdata' 
USER_DATA_IMAGES = 'static/userdata' 
def isValidImage(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in {'png', 'jpeg', 'jpg', 'webp', 'gif'}


@authBlueprint.route("/login", methods=['GET', 'POST'])
def loginUser():
    try:
        if "email" in session:
            return redirect(url_for('blog.listAllBlogs'))
        
        if request.method == 'POST':
            email = request.form.get('email')
            password = request.form.get('password')
            usercreds = userCollection.find_one({"email": email})
            if not(re.fullmatch(regex, email)):
                return render_template("auth/auth.html", type="login", error='Email is Invalid', formValues={'email': email, 'password': password})
            if usercreds:
                if (password == usercreds['password']):
                    session["email"] = email
                    return redirect(url_for('blog.listAllBlogs'))
                else:
                    return render_template("auth/auth.html", type="login", error='Password is incorrect', formValues={'email': email, 'password': password})
            else:
                return render_template("auth/auth.html", type="login", error='User not registered', formValues={'email': email, 'password': password})
        
        return render_template("auth/auth.html", type="login", formValues={'email': '', 'password': ''})
    except Exception as err:
        print("Error in /login: ", err)
        return render_template("error.html")

@authBlueprint.route("/signup", methods=['GET', 'POST'])
def registerUser():
    try:
        if request.method == 'POST':
            author_profile = request.files['author_profile']
            fname = request.form.get('fname')
            email = request.form.get('email')
            password = request.form.get('password')
            cpassword = request.form.get('cpassword')
            if not(re.fullmatch(regex, email)):
                return render_template("auth/auth.html", type="signup", error='Email is Invalid', formValues={'fname': fname, 'email': email, 'password': password, 'cpassword': cpassword})
            if password != cpassword:
                return render_template("auth/auth.html", type="signup", error='Password doesnt match', formValues={'fname': fname, 'email': email, 'password': password, 'cpassword': cpassword})
            if userCollection.find_one({'email': email}):
                return render_template("auth/auth.html", type="signup", error='User already exists', formValues={'fname': fname, 'email': email, 'password': password, 'cpassword': cpassword})
            if (re.fullmatch(regex, email) and password==cpassword and (author_profile and isValidImage(author_profile.filename))):
                user_directory = os.path.join(USER_DATA_IMAGES, email)
                if not os.path.exists(user_directory):
                    os.makedirs(user_directory)

                author_profile.save(os.path.join(user_directory, 'profile-image.'+ author_profile.filename.split('.')[1]))
                
                newUserId = userCollection.insert_one({
                    'author_profile': 'profile-image.'+ author_profile.filename.split('.')[1],
                    'full_name': fname,
                    'email': email,
                    'password': password
                })
                if newUserId:
                    return redirect(url_for('auth.loginUser'))
                else:
                    return render_template("auth/auth.html", type="signup", error='Unexpected error occured while creating account, please try again', formValues={'fname': '', 'email': '', 'password': '', 'cpassword': ''})            

        return render_template("auth/auth.html", type="signup", formValues={'fname': '', 'email': '', 'password': '', 'cpassword': ''})
    except Exception as err:
        print("Error in /signup: ", err)
        return render_template("error.html")


@authBlueprint.route("/logout")
def logoutUser():
    session.clear()
    return redirect(url_for('auth.loginUser'))