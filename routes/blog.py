from flask import Blueprint, render_template, redirect, url_for, session, request
from db.mongoDB import blogCollection, userCollection
from datetime import date
from bson import ObjectId
import os

blogBlueprint = Blueprint("blog", __name__, url_prefix="/blog")
BLOG_DATA_IMAGES = 'static/blogdata' 

@blogBlueprint.route('/', methods=['GET'])
def listAllBlogs():
    try:
        allBlogs = blogCollection.find({})
        return render_template("blog/listblogs.html", data=allBlogs, selfBlog=False)
    except Exception as err:
        print("Error in /blog: ", err)
        return render_template("error.html")
    
@blogBlueprint.route('/myBlogs', methods=['GET', 'POST'])
def listUserBlogs():
    if session and session["email"]:
        try:
            userBlogs = blogCollection.find({'author_email': session["email"]})
            return render_template("blog/listblogs.html", data=userBlogs, selfBlog=True)
        except Exception as err:
            print("Error in /myblogs: ", err)
            return render_template("error.html")
    else:
        return redirect(url_for('auth.loginUser'))

@blogBlueprint.route('/new', methods=['GET', 'POST'])
def newBlog():
    if session and session["email"]:
        try:
            if request.method == 'POST':
                userName = userCollection.find_one({'email': session['email']})['full_name']
                blogId = ObjectId()
                icon = request.files['icon']
                banner = request.files['banner']

                blog_directory = os.path.join(BLOG_DATA_IMAGES, str(blogId))
                if not os.path.exists(blog_directory):
                    os.makedirs(blog_directory)

                icon.save(
                    os.path.join(blog_directory, 'icon.webp')
                )
                icon.save(
                    os.path.join(blog_directory, 'banner.webp')
                )

                blog = {
                    '_id': blogId,
                    'author': userName,
                    'author_email': session['email'],
                    'date': date.today().strftime("%b %d, %y"),
                    'title': request.form.get('title'),
                    'icon': 'icon.webp',
                    'banner': 'banner.webp',
                    'content': request.form.get('ckeditor'),
                    'like_count': 0,
                    'comment_count': 0
                }
                if blog:
                    blogCollection.insert_one(blog)
                    redirect(url_for('blog.listAllBlogs'))
                else:
                    print("All fields are required")            
                
            return render_template("blog/newblog.html")
        except Exception as err:
            print("Error in /blog/new: ", err)
            return render_template("error.html")
    else:
        return redirect(url_for('auth.loginUser'))

@blogBlueprint.route('/edit/<int:blogId>', methods=['GET', 'POST'])
def editBlog(blogId):
    if session and session["email"]:
        try:
            userBlog = blogCollection.find_one({'_id': blogId})
            return render_template("blog/editblog.html", data=userBlog)
        except Exception as err:
            print(f"Error in /blog/edit/{blogId}: " , err)
            return render_template("error.html")
    else:
        return redirect(url_for('auth.loginUser'))

@blogBlueprint.route('/<blogId>', methods=['GET', 'POST'])
def viewBlog(blogId):
    if blogId:
        if session and session["email"]:
            try:
                blog = blogCollection.find_one({'_id': ObjectId(blogId)})
                if blog:
                    return render_template("blog/blogdetail.html", data=blog)
                else:
                    return redirect(url_for('blog.listAllBlogs'))    
            except Exception as err:
                print(f"Error in /blog/{blogId}: ", err)
                return render_template("login.html")
        else:
            return redirect(url_for('auth.loginUser'))
    else:
        return 