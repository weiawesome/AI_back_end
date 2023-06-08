import random
import string
from email.message import EmailMessage

from celery import Celery
from sqlalchemy import create_engine, MetaData, Table, update
from sqlalchemy.orm import scoped_session, sessionmaker
from models.User import User
from models.Access_token import Access_token
from models.Api_key import Api_key
from redis import Redis, ConnectionPool
from models.File import File
from utils import strid2byte
from ASR.ASR_Module import transcribe
from NLP.RevChat import revChat, revChat_test
from NLP.open_AI_chat import openaiChat, openaiChat_test
from OCR.Craft_TrOCR import image_to_texts
import os
from celery import Task
from email.mime.text import MIMEText
import smtplib

engine = create_engine('mysql+pymysql://{}:{}@mysql/{}'.format(os.environ.get('SQL_USER'),os.environ.get('SQL_PWD'),os.environ.get('DB_NAME')))
metadata = MetaData()
Session = scoped_session(sessionmaker(bind=engine))

REDIS_PASSWORD = os.getenv('REDIS_PASSWORD')
celery_app = Celery(
    "celery",
    broker="redis://:{}@redis:6379/1".format(REDIS_PASSWORD),
    backend="redis://:{}@redis:6379/2".format(REDIS_PASSWORD),
    result_expires=3600,
)

pool = ConnectionPool(host='redis', port=6379, db=0,password=REDIS_PASSWORD)

class DatabaseTask(Task):
    def on_success(self, retval, task_id, args, kwargs):
        session = Session()
        print('kwargs',kwargs)
        print('args',args)
        try:
            task_result = session.get(File, strid2byte(kwargs['id']))
            if task_result is not None:
                task_result.status = "SUCCESS"
                task_result.result = retval
                session.commit()
        except Exception as e:
            session.rollback()
            raise
        finally:
            Session.close()

    def on_failure(self, exc, task_id, args, kwargs, einfo):
        session = Session()  # 創建一個新的 session
        try:
            task_result = session.get(File, strid2byte(kwargs['id']))
            if task_result is not None:
                task_result.status = "FAILURE"
                session.commit()
        except Exception as e:
            session.rollback()
            raise
        finally:
            Session.close()


@celery_app.task(bind=True, base=DatabaseTask)
def ASR_predict(self,id,file, prompt,api_key,access_token):
    content = transcribe(file)
    status = revChat_test(access_token=access_token)
    response={'prompt':prompt,'content':content,'result':'','details':[]}
    if status:
        details, result = revChat(access_token=access_token, mode='ASR', prompt=prompt, text=content)
        response['result']=result
        response['details']=details
    return response


@celery_app.task(bind=True, base=DatabaseTask)
def OCR_predict(self,id,file, prompt,api_key,access_token):
    content = image_to_texts(file)
    response = {'prompt': prompt, 'content': content, 'result': '', 'details': []}
    if revChat_test(access_token=access_token):
        details, result = revChat(access_token=access_token, mode='OCR', prompt=prompt, text=content)
        response['result'] = result
        response['details'] = details
    return response

@celery_app.task(bind=True, base=DatabaseTask)
def NLP_edit_OCR(self,id, prompt, content,api_key,access_token):
    response = {'prompt': prompt, 'content': content, 'result': '', 'details': []}
    if revChat_test(access_token=access_token):
        details, result = revChat(access_token=access_token, mode='OCR', prompt=prompt, text=content)
        response['result'] = result
        response['details'] = details
    return response



@celery_app.task(bind=True, base=DatabaseTask)
def NLP_edit_ASR(self,id, prompt, content,api_key,access_token):
    response = {'prompt': prompt, 'content': content, 'result': '', 'details': []}
    if revChat_test(access_token=access_token):
        details, result = revChat(access_token=access_token, mode='ASR', prompt=prompt, text=content)
        response['result'] = result
        response['details'] = details
    return response


@celery_app.task(bind=True)
def Mail_sent(self,mail):
    redis_client = Redis(connection_pool=pool)
    code = ''.join(random.choice(string.ascii_letters + string.digits) for _ in range(6))
    email_body = """Hello,<br>
        Thank you for registering.<br><br>

        The Educational highlights and English writing learning aids can help you study more efficiently.<br>
        I hope you like it, and use it a lot.<br><br>

        If you encounter any problems, you can always write to us, <br>
        we are more than happy to improve and deal with it<br><br>

        <strong>您的驗證碼是 {}，請在10分鐘內在網站上輸入這個碼以完成驗證。</strong><br><br>
        Regards,<br>
        Study Savvy
        """.format(code)
    with smtplib.SMTP(host='smtp.gmail.com') as smtp:
        try:
            smtp.ehlo()
            smtp.starttls()
            smtp.login(os.getenv('USER_MAIL'), os.getenv('USER_PWD'))
            content = EmailMessage()
            sender_name='Study Savvy'
            content['From'] = f"{sender_name} <{os.getenv('USER_MAIL')}>"
            content['To'] = mail
            content['Subject'] = "StudySavvy 信箱認證 (Verification of email for StudySavvy)"
            content.set_content(email_body,'html')
            smtp.send_message(content)
        except Exception as e:
            print('Error to send the email!', e)
            return
        redis_client.set(mail, code)
        redis_client.expire(mail, 600)
    return