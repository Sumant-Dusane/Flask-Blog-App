from flask import Flask
from flask_ckeditor import CKEditor

from routes.home import homeBlueprint
from routes.auth import authBlueprint
from routes.blog import blogBlueprint

app = Flask(__name__)
app.config['SECRET_KEY'] = '3d6f45a5fc12445dbac2f59c3b6c7cb1' 

ckeditor = CKEditor(app)

app.register_blueprint(authBlueprint)
app.register_blueprint(blogBlueprint)
app.register_blueprint(homeBlueprint)