from flask import Blueprint, request
from flask_jwt_extended import jwt_required, get_jwt_identity
from webargs.flaskparser import use_args
from db import db
from models.Access_token import Access_token
from models.Api_key import Api_key
from models.User import User
from request_schema import Access_token_args, Api_key_args
from utils import in_blacklist

access_method_bp = Blueprint('Access_method', __name__)
@access_method_bp.route('/api/Access_method/access_token',methods=['PUT'])
@jwt_required()
@use_args(Access_token_args)
def Access_token_route(args):
    auth_header = request.headers.get('Authorization', None)
    result = True
    if auth_header:
        raw_jwt_headers = auth_header.split(' ')[1]
        result = result and in_blacklist(raw_jwt_headers)
        print(raw_jwt_headers)
    if 'access_token_cookie' in request.cookies:
        raw_jwt_cookie = request.cookies['access_token_cookie']
        result = result and in_blacklist(raw_jwt_cookie)
    if result:
        return '', 422
    current_user = get_jwt_identity()
    token = args['access_token']
    AES_key = args['AES_key']
    token_db = db.session.get(User, current_user).access_token
    if(token_db):
        token_db.token=token
        token_db.AES_key=AES_key
        db.session.commit()
    else:
        new_token = Access_token(mail=current_user,token=token,AES_key=AES_key)
        db.session.add(new_token)
        db.session.commit()
    return ''

@access_method_bp.route('/api/Access_method/api_key',methods=['PUT'])
@jwt_required()
@use_args(Api_key_args)
def Api_key_route(args):
    auth_header = request.headers.get('Authorization', None)
    result = True
    if auth_header:
        raw_jwt_headers = auth_header.split(' ')[1]
        result = result and in_blacklist(raw_jwt_headers)
        print(raw_jwt_headers)
    if 'access_token_cookie' in request.cookies:
        raw_jwt_cookie = request.cookies['access_token_cookie']
        result = result and in_blacklist(raw_jwt_cookie)
    if result:
        return '', 422
    current_user = get_jwt_identity()
    key = args['api_key']
    AES_key = args['AES_key']
    key_db = db.session.get(User, current_user).api_key
    if (key_db):
        key_db.key = key
        key_db.AES_key = AES_key
        db.session.commit()
    else:
        new_key = Api_key(mail=current_user, key=key, AES_key=AES_key)
        db.session.add(new_key)
        db.session.commit()
    return ''