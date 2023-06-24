import json
import os

import redis
from flask import Blueprint, request, send_from_directory
from flask_jwt_extended import jwt_required, get_jwt_identity
from sqlalchemy import and_, desc

from db import db
from models.File import File
from models.User import User
from response_schema import File_status, Files_response, Specific_File_response

from utils import is_valid_uuid, strid2byte,byte2strid


files_bp = Blueprint('Files', __name__)
redis_db_blacklist = redis.StrictRedis(host='redis', port=6379, db=3,password=os.getenv('REDIS_PASSWORD'))
@files_bp.route('/api/files', methods=['GET'])
@jwt_required()
def files():
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
    items_per_page = int(os.getenv('PAGE_NUMBER'))
    page_number = request.args.get('page', 1, type=int)
    page_number=max(1,page_number)
    total_pages=0
    files=[]
    if user:
        pagination = db.session.query(File).filter(
            File.mail == current_user
        ).order_by(
            desc(File.created_at)
        ).paginate(
            page=page_number, per_page=items_per_page, error_out=False
        )
        total_pages=pagination.pages
        files = pagination.items

    result_list = []
    for i in files:
        result_list.append(
            File_status(file_time=str(i.created_at), file_id=byte2strid(i.id), status=i.status, file_type=i.type))
    result = Files_response(total_pages=total_pages,current_page=page_number,datas=result_list)
    json_result = result.json(ensure_ascii=False)
    return json_result
@files_bp.route('/api/files/ASR', methods=['GET'])
@jwt_required()
def ASR_files():
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
    items_per_page = int(os.getenv('PAGE_NUMBER'))
    page_number = request.args.get('page', 1, type=int)
    page_number=max(1,page_number)
    total_pages = 0
    files = []
    if user:
        pagination = db.session.query(File).filter(
            File.mail == current_user,File.type=='ASR'
        ).order_by(
            desc(File.created_at)
        ).paginate(
            page=page_number, per_page=items_per_page, error_out=False
        )
        total_pages = pagination.pages
        files = pagination.items

    result_list = []
    for i in files:
        result_list.append(
            File_status(file_time=str(i.created_at), file_id=byte2strid(i.id), status=i.status, file_type=i.type))
    result = Files_response(total_pages=total_pages, current_page=page_number, datas=result_list)
    json_result = result.json(ensure_ascii=False)
    return json_result
@files_bp.route('/api/files/OCR', methods=['GET'])
@jwt_required()
def OCR_files():
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
    items_per_page = int(os.getenv('PAGE_NUMBER'))
    page_number = request.args.get('page', 1, type=int)
    page_number=max(1,page_number)
    total_pages = 0
    files = []
    if user:
        pagination = db.session.query(File).filter(
            File.mail == current_user, File.type == 'OCR'
        ).order_by(
            desc(File.created_at)
        ).paginate(
            page=page_number, per_page=items_per_page, error_out=False
        )
        total_pages = pagination.pages
        files = pagination.items

    result_list = []
    for i in files:
        result_list.append(
            File_status(file_time=str(i.created_at), file_id=byte2strid(i.id), status=i.status, file_type=i.type))
    result = Files_response(total_pages=total_pages, current_page=page_number, datas=result_list)
    json_result = result.json(ensure_ascii=False)
    return json_result
@files_bp.route('/api/files/<string:file_id>')
@jwt_required()
def Specific_File(file_id):
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
    json_result=result.json(ensure_ascii=False)
    return json_result


@files_bp.route('/api/files/<string:file_id>',methods=['DELETE'])
@jwt_required()
def Delete_Specific_File(file_id):
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
    if (is_valid_uuid(file_id)):
        file_id = strid2byte(file_id)
    else:
        return '', 400
    file = db.session.get(File, file_id)
    if (file):
        current_user = get_jwt_identity()
        if file.mail == current_user:
            os.remove(file.directory)
            db.session.delete(file)
            db.session.commit()
            return '',201
        else:
            return '', 403

    else:
        return '', 404

@files_bp.route('/api/files/resources/graph/<string:file_id>')
@jwt_required()
def graph_File(file_id):
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
    if (is_valid_uuid(file_id)):
        file_id = strid2byte(file_id)
    else:
        return '', 400
    file = db.session.get(File, file_id)
    if file:
        if file.type=='OCR':
            current_user = get_jwt_identity()
            if file.mail == current_user:
                filepath=file.directory
                directory = os.path.dirname(filepath)
                filename = os.path.basename(filepath)
                return send_from_directory(directory, filename)
            else:
                return '', 403
        else:
            return '',404
    return '', 404

@files_bp.route('/api/files/resources/audio/<string:file_id>')
@jwt_required()
def audio_File(file_id):
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
    if (is_valid_uuid(file_id)):
        file_id = strid2byte(file_id)
    else:
        return '', 400
    file = db.session.get(File, file_id)
    if file:
        if file.type=='ASR':
            current_user = get_jwt_identity()
            if file.mail == current_user:
                filepath=file.directory
                directory = os.path.dirname(filepath)
                filename = os.path.basename(filepath)
                return send_from_directory(directory, filename)
            else:
                return '', 403
        else:
            return '',404
    return '', 404


