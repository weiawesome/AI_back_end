from flask import Blueprint, request
from flask_jwt_extended import jwt_required, get_jwt_identity
from webargs.flaskparser import use_args
from request_schema import Edit_args

from db import db
from models.File import File
from models.User import User
from tasks import NLP_edit_ASR, NLP_edit_OCR
from utils import strid2byte, is_valid_uuid, byte2strid, decrypt,in_blacklist

nlp_edit_bp = Blueprint('NLP_edit', __name__)
@nlp_edit_bp.route('/api/NLP_edit/ASR/<string:file_id>',methods=['PUT'])
@use_args(Edit_args)
@jwt_required()
def ASR_NLP_edit(args,file_id):
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
    if (is_valid_uuid(file_id)):
        file_id = strid2byte(file_id)
    else:
        return '', 400
    file = db.session.get(File, file_id)
    if file:
        prompt = args['prompt']
        content = args['content']
        current_user = get_jwt_identity()
        if file.mail==current_user:
            user = db.session.get(User, current_user)
            db_access_token = user.access_token
            db_api_key = user.api_key
            if (db_access_token):
                access_token = decrypt(db_access_token.token, db_access_token.AES_key)
            else:
                access_token = ''
            if (db_api_key):
                api_key = decrypt(db_api_key.key, db_api_key.AES_key)
            else:
                api_key = ''
            NLP_edit_ASR.delay(id=byte2strid(file_id),prompt=prompt,content=content,api_key=api_key,access_token=access_token)
            file.status='PENDING'
            db.session.commit()
        else:
            return '',403
    else:
        return '',404
    
    return '',200
@nlp_edit_bp.route('/api/NLP_edit/OCR/<string:file_id>',methods=['PUT'])
@use_args(Edit_args)
@jwt_required()
def OCR_NLP_edit(args,file_id):
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
    if is_valid_uuid(file_id):
        file_id = strid2byte(file_id)
    else:
        return '', 400
    file = db.session.get(File, file_id)
    if file:
        prompt = args['prompt']
        content = args['content']
        current_user = get_jwt_identity()
        if file.mail == current_user:
            user = db.session.get(User, current_user)
            db_access_token = user.access_token
            db_api_key = user.api_key
            if (db_access_token):
                access_token = decrypt(db_access_token.token, db_access_token.AES_key)
            else:
                access_token = ''
            if (db_api_key):
                api_key = decrypt(db_api_key.key, db_api_key.AES_key)
            else:
                api_key = ''
            NLP_edit_OCR.delay(id=byte2strid(file_id), prompt=prompt, content=content, api_key=api_key,
                               access_token=access_token)
            file.status = 'PENDING'
            db.session.commit()
        else:
            return '', 403
    else:
        return '', 404
    return '', 200