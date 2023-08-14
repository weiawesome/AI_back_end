import hashlib
import os
import uuid
import time
import requests
from jose import jwt, jwk
from jose.utils import base64url_decode

def hash_password(password):
    # 生成随机盐值
    salt = os.urandom(16)
    # 创建 SHA-256 哈希对象
    sha256_hash = hashlib.sha256()
    # 将盐值与密码编码为 UTF-8 格式并进行哈希
    sha256_hash.update(salt + password.encode("utf-8"))
    # 获取哈希值的十六进制表示
    hashed_password = sha256_hash.hexdigest()
    # 返回哈希后的密码和盐值
    return hashed_password, salt

def verify_password(password, hashed_password, salt):
    # 创建 SHA-256 哈希对象
    sha256_hash = hashlib.sha256()
    # 将盐值与密码编码为 UTF-8 格式并进行哈希
    sha256_hash.update(salt + password.encode("utf-8"))
    # 获取哈希值的十六进制表示
    hashed_password_to_check = sha256_hash.hexdigest()
    return hashed_password_to_check==hashed_password
def is_valid_uuid(val):
    try:
        uuid.UUID(str(val))
        return True
    except ValueError:
        return False

def google_jwt_auth(id_token):
    response = requests.get("https://www.googleapis.com/oauth2/v3/certs")
    jwks = response.json()

    header = jwt.get_unverified_header(id_token)
    kid = header["kid"]

    rsa_key = next(item for item in jwks["keys"] if item["kid"] == kid)

    public_key = jwk.construct(rsa_key)
    message, encoded_signature = str(id_token).rsplit(".", 1)
    decoded_signature = base64url_decode(encoded_signature.encode())

    if not public_key.verify(message.encode(), decoded_signature):
        return False,""
    claims = jwt.get_unverified_claims(id_token)
    if time.time() > claims["exp"]:
        return False,""
    if claims["iss"]!="https://accounts.google.com" or claims["aud"]!=os.getenv("GOOGLE_CLIENT_ID"):
        return False,""
    return True,claims