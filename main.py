from flask import Flask

from routes.home import homeBlueprint
from routes.auth import authBlueprint
from routes.blog import blogBlueprint

app = Flask(__name__)

app.register_blueprint(homeBlueprint)
app.register_blueprint(authBlueprint)
app.register_blueprint(blogBlueprint)

app.run(debug=True)