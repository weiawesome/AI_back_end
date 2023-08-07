import redis
from flask import Blueprint, make_response, request
from db import db
from flask_jwt_extended import create_access_token, set_access_cookies, jwt_required, unset_jwt_cookies
from request_schema import Login_args,Signup_args
from webargs.flaskparser import use_args
from models.User import User
from response_schema import Login_response_app
from utils import verify_password, hash_password,google_jwt_auth
import env

user_bp = Blueprint("User", __name__)
redis_db_blacklist = redis.StrictRedis(host=env.REDIS_HOST, port=int(env.REDIS_PORT), db=int(env.REDIS_DB),password=env.REDIS_PASSWORD)
@user_bp.route("/api/login/web", methods=["POST"])
@use_args(Login_args)
def login_web(args):
    mail=args["mail"]
    pwd=args["password"]
    user = db.session.get(User, mail)
    if user is None:
        return "",401
    salt=user.salt
    hash_pwd=user.password
    if verify_password(pwd, hash_pwd, salt):
        token = create_access_token(identity=mail)
    else:
        return "",401
    response = make_response("")
    set_access_cookies(response, token)
    return response

@user_bp.route("/api/login/app", methods=["POST"])
@use_args(Login_args)
def login_app(args):
    mail=args["mail"]
    pwd=args["password"]
    user = db.session.get(User, mail)
    if user is None:
        return "", 401
    salt = user.salt
    hash_pwd = user.password
    if verify_password(pwd, hash_pwd, salt):
        token = create_access_token(identity=mail)
    else:
        return "", 401
    result = Login_response_app(token=token)
    json_result = result.json(ensure_ascii=False)
    return json_result

@user_bp.route("/api/logout",methods=["DELETE"])
@jwt_required()
def logout():
    auth_header = request.headers.get("Authorization", None)
    result = True
    if auth_header:
        raw_jwt_headers = auth_header.split(" ")[1]
        result = result and redis_db_blacklist.get(raw_jwt_headers)
    if "access_token_cookie" in request.cookies:
        raw_jwt_cookie = request.cookies["access_token_cookie"]
        result = result and redis_db_blacklist.get(raw_jwt_cookie)
    if result:
        return "", 422
    if auth_header:
        raw_jwt = auth_header.split(" ")[1]
        redis_db_blacklist.set(raw_jwt,"black_list",ex=60*60*24*int(env.JWT_EXPIRE_DAYS))
    if "access_token_cookie" in request.cookies:
        raw_jwt  = request.cookies["access_token_cookie"]
        redis_db_blacklist.set(raw_jwt,"black_list",ex=60*60*24*int(env.JWT_EXPIRE_DAYS))
    response = make_response("")
    unset_jwt_cookies(response)
    return response,201

@user_bp.route("/api/signup",methods=["POST"])
@use_args(Signup_args)
def signup(args):
    name=args["name"]
    gender = args["gender"]
    mail = args["mail"]
    pwd = args["password"]
    user = db.session.get(User, mail)
    if user is not None:
        return "",401
    hash_pwd,salt=hash_password(pwd)
    new_user = User(name=name, mail=mail, gender=gender, password=hash_pwd, salt=salt)
    db.session.add(new_user)
    db.session.commit()
    return ""
