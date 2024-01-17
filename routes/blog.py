from flask import Blueprint, render_template, redirect, url_for, session, request
from db.mongoDB import blogCollection, userCollection, commentCollection, likeCollection
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
                icon = request.files['icon']
                banner = request.files['banner']
                blog_directory = os.path.join(BLOG_DATA_IMAGES, str(blogId))
                if not os.path.exists(blog_directory):
                    os.makedirs(blog_directory)
                icon.save(
                    os.path.join(blog_directory, 'icon.webp')
                )
                banner.save(
                    os.path.join(blog_directory, 'banner.webp')
                )

                if blog:
                    blogCollection.insert_one(blog)
                    return redirect(url_for('blog.listAllBlogs'))
                else:
                    print("All fields are required")            
                
            return render_template("blog/newblog.html", data={}, edit=False)
        except Exception as err:
            print("Error in /blog/new: ", err)
            return render_template("error.html")
    else:
        return redirect(url_for('auth.loginUser'))

@blogBlueprint.route('/edit/<blogId>', methods=['GET', 'POST'])
def editBlog(blogId):
    if session and session["email"]:
        try:

            if request.method == 'POST':
                editedBlog = {
                    'date': date.today().strftime("%b %d, %y"),
                    'title': request.form.get('title'),
                    'content': request.form.get('ckeditor'),
                }

                icon = request.files['icon']
                banner = request.files['banner']
                blog_directory = os.path.join(BLOG_DATA_IMAGES, str(blogId))
                if not os.path.exists(blog_directory):
                    os.makedirs(blog_directory)
                icon.save(
                    os.path.join(blog_directory, 'icon.webp')
                )
                banner.save(
                    os.path.join(blog_directory, 'banner.webp')
                )

                blogCollection.update_one(
                    {
                        '_id': ObjectId(blogId)
                    }, {
                        '$set': editedBlog
                    }
                )

                return redirect(url_for('blog.viewBlog', blogId=blogId))

            userBlog = blogCollection.find_one({'_id': ObjectId(blogId)})
            return render_template("blog/newblog.html", data=userBlog, edit=True)
        except Exception as err:
            print(f"Error in /blog/edit/{blogId}: " , err)
            return render_template("error.html")
    else:
        return redirect(url_for('auth.loginUser'))

@blogBlueprint.route('/<blogId>', methods=['GET', 'POST'])
def viewBlog(blogId):
    if not blogId == None:
        if session and session["email"]:
            try:
                blog = blogCollection.find_one({'_id': ObjectId(blogId)})
                blogComment = commentCollection.find({'blogId': ObjectId(blogId)})
                
                return render_template("blog/blogdetail.html", data=blog, comments=blogComment)
            except Exception as err:
                print(f"Error in /blog/{blogId}: ", err)
                return redirect(url_for('blog.listAllBlogs'))
        else:
            return redirect(url_for('auth.loginUser'))
    else:
        return 
    

@blogBlueprint.route('/delete/<blogId>', methods=['GET', 'POST'])
def deleteBlog(blogId):
    if session and session['email']:
        try:
            blogCollection.delete_one({'_id': ObjectId(blogId)})
            commentCollection.delete_many({'blogId': ObjectId(blogId)})
            likeCollection.delete_many({'blogId': ObjectId(blogId)})
            return redirect(url_for('blog.listAllBlogs'))
        except Exception as err:
            print(f"Error in /blog/delete/{blogId}: ", err)
            return render_template(url_for('blog.viewBlog', blogId=blogId))
    

@blogBlueprint.route('/comment/<blogId>', methods=['GET', 'POST'])
def addComment(blogId):
    newComment = {
        'commentor': userCollection.find_one({'email': session['email']})['full_name'],
        'commentor_email': session['email'],
        'date': date.today().strftime("%b %d, %y"),
        'comment': request.form.get('new-comment'),
        'blogId': ObjectId(blogId)
    }
    newCommentId = commentCollection.insert_one(newComment)
    if newCommentId:
        blogCollection.update_one(
            # condition
            {
                '_id': ObjectId(blogId)
            },
            # operation
            {
                '$inc': {
                    'comment_count': 1
                }
            }
        )
        #  re-render the template when new comment is added
        return redirect(url_for('blog.viewBlog', blogId=blogId))
    else:
        print("Unexpected error occured, please try again")
        return
    
@blogBlueprint.route('/like/<blogId>', methods=['GET', 'POST'])
def likeBlog(blogId):
    isLiked = likeCollection.find_one({'user': session['email']})
    if isLiked:
        likeCollection.delete_one({'user': session['email']})
        blogCollection.update_one(
            {
                '_id': ObjectId(blogId)
            }, {
                '$inc': {
                    'like_count': -1
                }
            }
        )
    else:
        newLike = {
            'user': session['email'],
            'blogId': ObjectId(blogId),
        }
        likeCollection.insert_one(newLike)
        blogCollection.update_one(
            {
                '_id': ObjectId(blogId)
            },
            {
                '$inc': {
                    'like_count': 1
                }
            }
        )
    return redirect(url_for('blog.listAllBlogs', blogId=blogId))