import io
import os
import uuid
from flask import Blueprint, request
from flask_jwt_extended import jwt_required, get_jwt_identity
from werkzeug.utils import secure_filename
from db import db
from models.File import File
from models.User import User
from utils import decrypt, strid2byte,in_blacklist
from tasks import ASR_predict,OCR_predict

ai_predict_bp = Blueprint('AI_predict', __name__)
@ai_predict_bp.route('/api/predict/ASR', methods=['POST'])
@jwt_required()
def ASR_predict_route():
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
        if file_type=='mp3':
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
        result = result and in_blacklist(raw_jwt_headers)
        print(raw_jwt_headers)
    if 'access_token_cookie' in request.cookies:
        raw_jwt_cookie = request.cookies['access_token_cookie']
        result = result and in_blacklist(raw_jwt_cookie)
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
