from flask_pymongo import pymongo 

MONGO_URI = 'mongodb+srv://sumant-dusane:sumant123456@sumant-dusane.3donyvz.mongodb.net/?retryWrites=true&w=majority'
mongo_client = pymongo.MongoClient(MONGO_URI)
mongo = mongo_client.blog_app

blogCollection = mongo.blogs
userCollection = mongo.users
commentCollection = mongo.comments
likeCollection = mongo.likes