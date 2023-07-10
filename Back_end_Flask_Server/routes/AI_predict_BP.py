import io
import os
import uuid

import redis
from flask import Blueprint, request
from flask_jwt_extended import jwt_required, get_jwt_identity
from webargs.flaskparser import use_args
from werkzeug.utils import secure_filename
from db import db
from models.File import File
from models.User import User
from utils import decrypt, strid2byte
from tasks import ASR_predict,OCR_predict,OCR_predict_Text
from request_schema import OCR_Text_args

ai_predict_bp = Blueprint('AI_predict', __name__)
redis_db_blacklist = redis.StrictRedis(host='redis', port=6379, db=3,password=os.getenv('REDIS_PASSWORD'))
@ai_predict_bp.route('/api/predict/ASR', methods=['POST'])
@jwt_required()
def ASR_predict_route():
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
    output_path='/original_audio'
    if 'file' not in request.files:
        return 'No file part', 400
    file = request.files['file']
    prompt = request.form.get('prompt', '')

    if file.filename == '':
        return 'No selected file', 400
    if file:
        filename = secure_filename(file.filename)
        file_type=filename.split('.')[-1]
        if file_type=='mp3' or file_type=='m4a' or file_type=='wav':
            id = str(uuid.uuid4())
            filepath = os.path.join(output_path, id+'.mp3')
            file.save(filepath)
            current_user = get_jwt_identity()
            user = db.session.get(User, current_user)
            db_access_token=user.access_token
            db_api_key=user.api_key
            if(db_access_token):
                access_token=decrypt(db_access_token.token,db_access_token.AES_key)
            else:
                access_token=''
            if (db_api_key):
                api_key = decrypt(db_api_key.key, db_api_key.AES_key)
            else:
                api_key = ''
            ASR_predict.delay(id=id,file=filepath,prompt=prompt,api_key=api_key,access_token=access_token)
            result_id=strid2byte(id)
            new_file=File(id=result_id,mail=user.mail,status='PENDING',type='ASR',directory=filepath)
            db.session.add(new_file)
            db.session.commit()
            return '',200
        return 'File uploaded successfully, but not correct format.', 200
    else:
        return 'File type not allowed', 400
@ai_predict_bp.route('/api/predict/OCR', methods=['POST'])
@jwt_required()
def OCR_predict_route():
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
    output_path='/original_graph'
    if 'file' not in request.files:
        return 'No file part', 400
    file = request.files['file']
    prompt = request.form.get('prompt', '')

    if file.filename == '':
        return 'No selected file', 400
    if file:
        filename = secure_filename(file.filename)
        file_type = filename.split('.')[-1]
        if file_type=='jpg' or file_type=='jpeg' or file_type=='png':
            id = str(uuid.uuid4())
            filepath = os.path.join(output_path, id+'.'+file_type)
            file.save(filepath)
            current_user = get_jwt_identity()
            user = db.session.get(User, current_user)
            db_access_token=user.access_token
            db_api_key=user.api_key
            if(db_access_token):
                access_token=decrypt(db_access_token.token,db_access_token.AES_key)
            else:
                access_token=''
            if (db_api_key):
                api_key = decrypt(db_api_key.key, db_api_key.AES_key)
            else:
                api_key = ''
            OCR_predict.delay(id=id,file=filepath,prompt=prompt,api_key=api_key,access_token=access_token)
            result_id=strid2byte(id)
            new_file=File(id=result_id,mail=user.mail,status='PENDING',type='OCR',directory=filepath)
            db.session.add(new_file)
            db.session.commit()
            return '',200
        return 'File uploaded successfully, but not correct format. {}'.format(file_type), 200
    else:
        return 'File type not allowed', 400


@ai_predict_bp.route('/api/predict/OCR_Text', methods=['POST'])
@use_args(OCR_Text_args)
@jwt_required()
def OCR_predict_Text_route(args):
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
    content=args['content']
    prompt=args['prompt']
    current_user = get_jwt_identity()
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
    OCR_predict_Text.delay(id=id,content=content , prompt=prompt, api_key=api_key, access_token=access_token)
    result_id = strid2byte(id)
    new_file = File(id=result_id, mail=user.mail, status='PENDING', type='OCR', directory="NULL")
    db.session.add(new_file)
    db.session.commit()
    return '', 200


