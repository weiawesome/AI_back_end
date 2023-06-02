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
from celery import Task
import os

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
    pass


@celery_app.task(bind=True, base=DatabaseTask)
def OCR_predict(self,id,file, prompt,api_key,access_token):
    pass
@celery_app.task(bind=True, base=DatabaseTask)
def NLP_edit_OCR(self,id, prompt, content,api_key,access_token):
    pass



@celery_app.task(bind=True, base=DatabaseTask)
def NLP_edit_ASR(self,id, prompt, content,api_key,access_token):
    pass


@celery_app.task(bind=True)
def Mail_sent(self,mail):
    pass