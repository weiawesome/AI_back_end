import base64
import hashlib
import os
import uuid

from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.asymmetric import padding
from cryptography.hazmat.backends import default_backend
from Crypto.Cipher import AES
from Crypto.Util.Padding import unpad

import time
import requests
from jose import jwt, jwk
from jose.utils import base64url_decode
def rotate_image_based_on_exif(image):
    try:
        exif_data = image._getexif()
        if exif_data:
            orientation_tag = 0x0112
            if orientation_tag in exif_data:
                orientation = exif_data[orientation_tag]
                if orientation == 3:
                    image = image.rotate(180,expand=True)
                elif orientation == 6:
                    image = image.rotate(-90,expand=True)
                elif orientation == 8:
                    image = image.rotate(90,expand=True)
    except AttributeError:
        print(AttributeError.name)

    return image

def hash_password(password):
    # 生成随机盐值
    salt = os.urandom(16)
    # 创建 SHA-256 哈希对象
    sha256_hash = hashlib.sha256()
    # 将盐值与密码编码为 UTF-8 格式并进行哈希
    sha256_hash.update(salt + password.encode('utf-8'))
    # 获取哈希值的十六进制表示
    hashed_password = sha256_hash.hexdigest()
    # 返回哈希后的密码和盐值
    return hashed_password, salt

def verify_password(password, hashed_password, salt):
    # 创建 SHA-256 哈希对象
    sha256_hash = hashlib.sha256()
    # 将盐值与密码编码为 UTF-8 格式并进行哈希
    sha256_hash.update(salt + password.encode('utf-8'))
    # 获取哈希值的十六进制表示
    hashed_password_to_check = sha256_hash.hexdigest()
    return hashed_password_to_check==hashed_password
def is_valid_uuid(val):
    try:
        uuid.UUID(str(val))
        return True
    except ValueError:
        return False
def strid2byte(id):
    str_id=str(id)
    uuid_id=uuid.UUID(str_id)
    return uuid_id.bytes
def byte2strid(id):
    uuid_id=uuid.UUID(bytes=id)
    return str(uuid_id)
def base642byte(data):
    original_bytes_data = base64.b64decode(data)
    return original_bytes_data

def RSA_decrypt(encrypted_aes_key):
    with open('/Security/private_key.pem', 'rb') as f:
        pem_private = f.read()
    private_key = serialization.load_pem_private_key(
        pem_private,
        password=None,
        backend=default_backend()
    )
    aes_key = private_key.decrypt(
        encrypted_aes_key,
        padding.OAEP(
            mgf=padding.MGF1(algorithm=hashes.SHA256()),
            algorithm=hashes.SHA256(),
            label=None
        )
    )
    return aes_key

def AES_decrypt(aes_key,encrypted_data):
    cipher_dec = AES.new(aes_key, AES.MODE_ECB)
    data_pad_dec = cipher_dec.decrypt(encrypted_data)
    data = unpad(data_pad_dec, AES.block_size)
    result = data.decode()
    return result

def decrypt(encrypted_data,encrypted_key):
    origin_key=base642byte(encrypted_key)
    key=RSA_decrypt(origin_key)
    origin_key=base642byte(key)
    origin_data=base642byte(encrypted_data)
    result=AES_decrypt(origin_key,origin_data)
    return result

def google_jwt_auth(id_token):
    response = requests.get('https://www.googleapis.com/oauth2/v3/certs')
    jwks = response.json()

    header = jwt.get_unverified_header(id_token)
    kid = header['kid']

    rsa_key = next(item for item in jwks['keys'] if item["kid"] == kid)

    public_key = jwk.construct(rsa_key)
    message, encoded_signature = str(id_token).rsplit('.', 1)
    decoded_signature = base64url_decode(encoded_signature.encode())

    if not public_key.verify(message.encode(), decoded_signature):
        return False,''
    claims = jwt.get_unverified_claims(id_token)
    if time.time() > claims['exp']:
        return False,''
    if claims['iss']!='https://accounts.google.com' or claims['aud']!=os.getenv('GOOGLE_CLIENT_ID'):
        return False,''
    return True,claims