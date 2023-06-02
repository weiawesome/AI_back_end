import json

from flask import Blueprint, request
from flask_jwt_extended import jwt_required, get_jwt_identity
from sqlalchemy import and_

from db import db
from models.File import File
from models.User import User
from response_schema import File_status, Files_response, Specific_File_response

from utils import is_valid_uuid, strid2byte,byte2strid,in_blacklist


files_bp = Blueprint('Files', __name__)
@files_bp.route('/api/files', methods=['GET'])
@jwt_required()
def files():
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
    user = db.session.get(User, current_user)
    files=user.files
    result_list=[]
    for i in files:
        result_list.append(File_status(file_time=str(i.created_at),file_id=byte2strid(i.id),status=i.status,file_type=i.type))
    result = Files_response(datas=result_list)
    json_result = result.json()
    return json_result
@files_bp.route('/api/files/ASR', methods=['GET'])
@jwt_required()
def ASR_files():
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
    files = db.session.query(File).filter(and_(File.mail == current_user, File.type == 1)).all()
    result_list = []
    for i in files:
        result_list.append(File_status(file_time=str(i.created_at), file_id=byte2strid(i.id), status=i.status, file_type=i.type))
    result = Files_response(datas=result_list)
    json_result = result.json()
    return json_result
@files_bp.route('/api/files/OCR', methods=['GET'])
@jwt_required()
def OCR_files():
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
    files = db.session.query(File).filter(and_(File.mail == current_user, File.type == 0)).all()
    result_list = []
    for i in files:
        result_list.append(File_status(file_time=str(i.created_at), file_id=byte2strid(i.id), status=i.status, file_type=i.type))
    result = Files_response(datas=result_list)
    json_result = result.json()
    return json_result
@files_bp.route('/api/files/ASR/<string:file_id>')
@jwt_required()
def ASRFile(file_id):
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
    if(is_valid_uuid(file_id)):
        file_id=strid2byte(file_id)
    else:
        return '',400
    file=db.session.get(File,file_id)
    if(file):
        current_user = get_jwt_identity()
        if file.mail==current_user:
            if file.status == 'SUCCESS':
                result = file.result
                result = Specific_File_response(prompt=result['prompt'], content=result['content'],
                                                summarize=result['result'], details=result['details'])
            else:
                return '',404
        else:
            return '',403

    else:
        return '',404
    json_result=result.json()
    return json_result
@files_bp.route('/api/files/OCR/<string:file_id>')
@jwt_required()
def OCRFile(file_id):
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
    if (file):
        current_user = get_jwt_identity()
        if file.mail == current_user:
            if file.status=='SUCCESS':
                result = file.result
                result = Specific_File_response(prompt=result['prompt'],
                                            content=result['content'],
                                            summarize=result['result'], details=result['details'])
            else:
                return '',404
        else:
            return '',403
    else:
        result = Specific_File_response(prompt='', content='', summarize='', details=[''])
    json_result = result.json()
    return json_result
