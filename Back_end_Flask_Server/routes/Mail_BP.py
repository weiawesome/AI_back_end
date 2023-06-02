import redis
from flask import Blueprint
from webargs.flaskparser import use_args

from request_schema import Email_args
from tasks import Mail_sent

mail_bp = Blueprint('Mail', __name__)
redis_db_mail = redis.StrictRedis(host='redis', port=6379, db=0)
@mail_bp.route('/api/verification', methods=['POST'])
@use_args(Email_args)
def verification(args):
    mail=args['mail']
    Mail_sent.delay(mail=mail)
    return ''

@mail_bp.route('/api/verification/<string:mail>/<string:code>')
def Mail_Verification(mail,code):
    verification_code=redis_db_mail.get(mail)
    if verification_code:
        if verification_code.decode()==code:
            return '',200
    return '',404