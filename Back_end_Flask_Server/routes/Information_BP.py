import os

import redis
from flask import Blueprint, request
from flask_jwt_extended import jwt_required, get_jwt_identity
from webargs.flaskparser import use_args
from db import db
from models.User import User
from request_schema import Information_args,Password_Edit_args
from response_schema import Information_response
from utils import verify_password, hash_password

information_bp = Blueprint('Information', __name__)
redis_db_blacklist = redis.StrictRedis(host='redis', port=6379, db=3,password=os.getenv('REDIS_PASSWORD'))
@information_bp.route('/api/information', methods=['GET'])
@jwt_required()
def information():
    auth_header = request.headers.get('Authorization', None)
    result = True
    if auth_header:
        raw_jwt_headers = auth_header.split(' ')[1]
        result = result and redis_db_blacklist.get(raw_jwt_headers)
    if 'access_token_cookie' in request.cookies:
        raw_jwt_cookie = request.cookies['access_token_cookie']
        result = result and redis_db_blacklist.get(raw_jwt_cookie)
    if result:
        return '', 422
    current_user = get_jwt_identity()
    user = db.session.get(User, current_user)
    if user == None:
        return '', 404
    result =Information_response(name=user.name,mail=user.mail,gender=user.gender)
    json_result = result.json(ensure_ascii=False)
    return json_result

@information_bp.route('/api/information/', methods=['PUT'])
@jwt_required()
@use_args(Information_args)
def information_update(args):
    auth_header = request.headers.get('Authorization', None)
    result = True
    if auth_header:
        raw_jwt_headers = auth_header.split(' ')[1]
        result = result and redis_db_blacklist.get(raw_jwt_headers)
    if 'access_token_cookie' in request.cookies:
        raw_jwt_cookie = request.cookies['access_token_cookie']
        result = result and redis_db_blacklist.get(raw_jwt_cookie)
    if result:
        return '', 422
    current_user = get_jwt_identity()
    user = db.session.get(User, current_user)
    if user == None:
        return '', 404
    name=args['name']
    gender=args['gender']
    user.name=name
    user.gender=gender
    db.session.commit()
    return '',200

@information_bp.route('/api/information/password_edit', methods=['PUT'])
@jwt_required()
@use_args(Password_Edit_args)
def password_edit(args):
    auth_header = request.headers.get('Authorization', None)
    result = True
    if auth_header:
        raw_jwt_headers = auth_header.split(' ')[1]
        result = result and redis_db_blacklist.get(raw_jwt_headers)
    if 'access_token_cookie' in request.cookies:
        raw_jwt_cookie = request.cookies['access_token_cookie']
        result = result and redis_db_blacklist.get(raw_jwt_cookie)
    if result:
        return '', 422
    current_user = get_jwt_identity()
    user = db.session.get(User, current_user)
    if user == None:
        return '', 404
    original_pwd=args['original_pwd']
    new_pwd = args['new_pwd']
    salt = user.salt
    hash_pwd = user.pwd
    if (verify_password(original_pwd, hash_pwd, salt)):
        hash_pwd, salt = hash_password(new_pwd)
        user.salt=salt
        user.pwd=hash_pwd
    else:
        return '', 401
    db.session.commit()
    return '',200