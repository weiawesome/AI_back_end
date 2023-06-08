from flask import Blueprint, make_response, request, url_for, redirect
from flask_jwt_extended import create_access_token, set_access_cookies

from db import db
from models.User import User
from oauth import oauth

from response_schema import Login_response_app
from utils import google_jwt_auth

oauth_bp = Blueprint('Oauth', __name__)

@oauth_bp.route('/api/oauth/web/google')
def signin_web_google():
    google = oauth.create_client('google')
    redirect_uri = url_for('Oauth.authorize_google', _external=True)
    redirect_uri=redirect_uri.replace('http','https')
    return google.authorize_redirect(redirect_uri,prompt='select_account')
@oauth_bp.route('/api/oauth/authorize/google', methods=['GET'])
def authorize_google():
    try:
        google = oauth.create_client('google')
        token = google.authorize_access_token()
        resp = google.get('userinfo')
        user_info = resp.json()
        name=user_info['name']
        avatar=user_info['picture']
        mail=user_info['email']
        gender='other'
        resp = google.get('https://people.googleapis.com/v1/people/me?personFields=genders')
        if resp.status_code == 200:
            gender_info = resp.json()
            gender_value=gender_info['genders'][-1]['value']
            if gender_value=='male' or gender_value=='female':
                gender=gender_value
        user = db.session.get(User, mail)
        if (user == None):
            new_user = User(name=name, mail=mail, gender=gender)
            db.session.add(new_user)
            db.session.commit()
        response = make_response(redirect('/'))
        token = create_access_token(identity=mail)
        set_access_cookies(response, token)
        return response
    except:
        return '',400
@oauth_bp.route('/api/oauth/app/google',methods=['GET'])
def signin_app_google():
    auth_header = request.headers.get('Authorization', None)
    if auth_header:
        raw_jwt_headers = auth_header.split(' ')[1]
        result, claims = google_jwt_auth(raw_jwt_headers)
        if not result:
            return '', 422
        mail = claims['email']
        name=claims['name']
        user = db.session.get(User, mail)
        if user == None:
            new_user = User(name=name, mail=mail)
            db.session.add(new_user)
            db.session.commit()
        token = create_access_token(identity=mail)
        gender = user.gender
        name = user.name
        result = Login_response_app(name=name, gender=gender, token=token)
        json_result = result.json(ensure_ascii=False)
        return json_result
    else:
        return '', 401