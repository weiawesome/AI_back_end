import os
from datetime import timedelta
from flask import Flask
from flasgger import Swagger
from oauth import oauth
from routes.Information_BP import information_bp
from routes.Oauth_BP import oauth_bp
from routes.AI_predict_BP import ai_predict_bp
from routes.Access_method_BP import access_method_bp
from routes.Files_BP import files_bp
from routes.Mail_BP import mail_bp
from routes.NLP_edit_BP import nlp_edit_bp
from routes.User_BP import user_bp
from db import db
from flask_jwt_extended import JWTManager
from models.User import User
from models.File import File
from models.Api_key import Api_key
from models.Access_token import Access_token

##############################################################################
#                           Set app (in flask)                               #
##############################################################################

app = Flask(__name__)

##############################################################################
#                          Set oauth (in flask)                              #
##############################################################################

app.secret_key = os.getenv('SECRET_KEY')
app.config.update(PREFERRED_URL_SCHEME='https')
oauth.init_app(app)

##############################################################################
#                           Set JWT setting                                  #
##############################################################################

app.config['JWT_SECRET_KEY'] = os.environ.get('JWT_SECRET_KEY')
app.config['JWT_ACCESS_TOKEN_EXPIRES'] = timedelta(days=int(os.getenv('EXPIRE_DAYS')))
app.config.update(
    SESSION_COOKIE_HTTPONLY=True
)
app.config['JWT_TOKEN_LOCATION'] = ['headers', 'cookies']
app.config['JWT_COOKIE_SECURE']=True
jwt = JWTManager(app)

##############################################################################
#                  Set swagger(open api document) setting                    #
##############################################################################

app.config['SWAGGER'] = {
    'openapi': '3.0.0'
}
swagger_config = {
    "headers": [],
    "specs": [
        {
            "endpoint": '/api/apispec',
            "route": '/api/docs/apispec.json',
        }
    ],
    "static_url_path": "/api/flasgger_static",
    "swagger_ui": True,
    "specs_route": "/api/docs/"
}
swagger = Swagger(app, config=swagger_config, template_file='openapi.yaml')

##############################################################################
#                           Set SQL(my-sql) DB                               #
##############################################################################

app.config['SQLALCHEMY_DATABASE_URI'] = \
    'mysql+pymysql://{}:{}@mysql/{}' \
        .format(
        os.environ.get('SQL_USER'),
        os.environ.get('SQL_PWD'),
        os.environ.get('DB_NAME')
    )
app.config['SQLALCHEMY_POOL_RECYCLE'] = 299
db.init_app(app)
with app.app_context():
    db.create_all()

##############################################################################
#                           Set route of User                                #
##############################################################################

app.register_blueprint(user_bp)

##############################################################################
#                         Set route of NLP_edit                              #
##############################################################################

app.register_blueprint(nlp_edit_bp)

##############################################################################
#                       Set route of Access_method                           #
##############################################################################

app.register_blueprint(access_method_bp)

##############################################################################
#                           Set route of Mail                                #
##############################################################################

app.register_blueprint(mail_bp)

##############################################################################
#                          Set route of Files                                #
##############################################################################

app.register_blueprint(files_bp)

##############################################################################
#                       Set route of AI_predict                              #
##############################################################################

app.register_blueprint(ai_predict_bp)

##############################################################################
#                          Set route of Oauth                                #
##############################################################################

app.register_blueprint(oauth_bp)

##############################################################################
#                       Set route of Information                             #
##############################################################################

app.register_blueprint(information_bp)

##############################################################################
#                           Set error handler                                #
##############################################################################
@app.errorhandler(422)
def handle_bad_request(err):
    return '', 400
