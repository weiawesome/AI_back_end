import redis
from flask import Blueprint
from webargs.flaskparser import use_args
from request_schema import Email_args
from tasks import Mail_sent
import env

mail_bp = Blueprint("Mail", __name__)
redis_db_mail = redis.StrictRedis(host=env.REDIS_HOST, port=int(env.REDIS_PORT), db=int(env.REDIS_DB),password=env.REDIS_PASSWORD)
@mail_bp.route("/api/Mail/verification", methods=["POST"])
@use_args(Email_args)
def verification(args):
    mail=args["mail"]
    Mail_sent.delay(mail=mail)
    return ""

@mail_bp.route("/api/Mail/verification/<string:mail>/<string:code>")
def Mail_Verification(mail,code):
    verification_code=redis_db_mail.get(mail)
    if verification_code:
        if verification_code.decode()==code:
            return "",200
    return "",404