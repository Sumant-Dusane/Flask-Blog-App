from flask import Blueprint, render_template

blogBlueprint = Blueprint("blog", __name__, url_prefix="/blog")

@blogBlueprint.route('/')
def listAllBlogs():
    try:
        return render_template("blog/listblogs.html")
    except Exception as err:
        print("Error in /blog: ", err)
        return render_template("error.html")

@blogBlueprint.route('/new')
def newBlog():
    try:
        return render_template("blog/newblog.html")
    except Exception as err:
        print("Error in /blog/new: ", err)
        return render_template("error.html")

@blogBlueprint.route('/edit/<int:blogId>')
def editBlog(blogId):
    try:
        return render_template("blog/editblog.html", blogId=blogId)
    except Exception as err:
        print(f"Error in /blog/edit/{blogId}: " , err)
        return render_template("error.html")

@blogBlueprint.route('/<int:blogId>')
def viewBlog(blogId):
    try:
        return render_template("blog/blogdetail.html", blogId=blogId)
    except Exception as err:
        print(f"Error in /blog/{blogId}: ", err)
        return render_template("error.html")