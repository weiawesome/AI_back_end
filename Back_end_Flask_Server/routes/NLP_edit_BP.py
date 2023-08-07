import redis
from flask import Blueprint, request
from flask_jwt_extended import jwt_required, get_jwt_identity
from webargs.flaskparser import use_args
from request_schema import Edit_args
from db import db
from models.File import File
from models.User import User
from tasks import NLP_edit_ASR, NLP_edit_OCR
from utils import strid2byte, is_valid_uuid, byte2strid, decrypt
import env


nlp_edit_bp = Blueprint("NLP_edit", __name__)
redis_db_blacklist = redis.StrictRedis(host=env.REDIS_HOST, port=int(env.REDIS_PORT), db=int(env.REDIS_DB),password=env.REDIS_PASSWORD)
@nlp_edit_bp.route("/api/NLP_edit/ASR/<string:file_id>",methods=["PUT"])
@use_args(Edit_args)
@jwt_required()
def ASR_NLP_edit(args,file_id):
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
    if not is_valid_uuid(file_id):
        return "", 400
    file = db.session.get(File, file_id)
    if file:
        prompt = args["prompt"]
        content = args["content"]
        current_user = get_jwt_identity()
        if file.user_mail==current_user:
            user = db.session.get(User, current_user)
            db_access_token = user.access_token
            db_api_key = user.api_key

            NLP_edit_ASR.delay(id=file_id,prompt=prompt,content=content,api_key=db_api_key.key,access_token=db_access_token.token,key_api_key=db_api_key.AES_key,key_access_token=db_access_token.AES_key)
            file.status="PENDING"
            db.session.commit()
        else:
            return "",403
    else:
        return "",404
    
    return "",200
@nlp_edit_bp.route("/api/NLP_edit/OCR/<string:file_id>",methods=["PUT"])
@use_args(Edit_args)
@jwt_required()
def OCR_NLP_edit(args,file_id):
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
    if not is_valid_uuid(file_id):
        return "", 400
    file = db.session.get(File, file_id)
    if file:
        prompt = args["prompt"]
        content = args["content"]
        current_user = get_jwt_identity()
        if file.user_mail == current_user:
            user = db.session.get(User, current_user)
            db_access_token = user.access_token
            db_api_key = user.api_key

            NLP_edit_OCR.delay(id=file_id, prompt=prompt, content=content, api_key=db_api_key.key,access_token=db_access_token.token,key_api_key=db_api_key.AES_key,key_access_token=db_access_token.AES_key)
            file.status = "PENDING"
            db.session.commit()
        else:
            return "", 403
    else:
        return "", 404
    return "", 200