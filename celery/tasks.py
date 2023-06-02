import random
import string
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
from email.mime.application import MIMEApplication
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
import smtplib
from email.mime.image import MIMEImage

engine = create_engine('mysql+pymysql://{}:{}@mysql/{}'.format(os.environ.get('SQL_USER'),os.environ.get('SQL_PWD'),os.environ.get('DB_NAME')))
metadata = MetaData()
Session = scoped_session(sessionmaker(bind=engine))

celery_app = Celery(
    "celery",
    broker="redis://redis:6379/1",
    backend="redis://redis:6379/2",
    result_expires=3600, )

pool = ConnectionPool(host='redis', port=6379, db=0)

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
    email_body = f'您的驗證碼是 {code}，請在10分鐘內在網站上輸入這個碼以完成驗證。'
    with smtplib.SMTP(host='smtp.gmail.com') as smtp:
        try:
            smtp.ehlo()
            smtp.starttls()
            smtp.login(os.getenv('USER_MAIL'), os.getenv('USER_PWD'))
            content = MIMEMultipart()
            content['to'] = mail
            content['subject'] = "StudySavvy 信箱認證 (Registration of StudySavvy)"
            content.attach(MIMEText(email_body))
            smtp.send_message(content)
        except Exception as e:
            print('Error to send the email!', e)
            return
        redis_client.set(mail, code)
        redis_client.expire(mail, 600)
    return