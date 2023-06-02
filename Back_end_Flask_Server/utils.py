import base64
import hashlib
import os
import uuid

import redis
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.asymmetric import padding
from cryptography.hazmat.backends import default_backend
from Crypto.Cipher import AES
from Crypto.Util.Padding import unpad
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

def in_blacklist(jwt):
    redis_db_blacklist = redis.StrictRedis(host='redis', port=6379, db=3)
    result=True if redis_db_blacklist.get(jwt) else False
    redis_db_blacklist.close()
    return result