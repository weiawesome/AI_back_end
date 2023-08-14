from celery import Celery
from sqlalchemy import create_engine, MetaData
from sqlalchemy.orm import scoped_session, sessionmaker
from redis import ConnectionPool
from models.File import File
from celery import Task
import env

dsn="mysql+pymysql://{}:{}@{}/{}".format(env.MYSQL_USER, env.MYSQL_PASSWORD, env.MYSQL_ADDRESS, env.MYSQL_DB)

engine = create_engine(dsn)
metadata = MetaData()
Session = scoped_session(sessionmaker(bind=engine))

REDIS_PASSWORD = env.REDIS_PASSWORD
REDIS_ADDRESS  =  env.REDIS_ADDRESS
REDIS_HOST  =  env.REDIS_HOST
REDIS_PORT  =  env.REDIS_PORT
REDIS_DB  =  env.REDIS_DB

celery_app = Celery(
    "celery",
    broker="redis://:{}@{}/{}".format(REDIS_PASSWORD,REDIS_ADDRESS,REDIS_DB),
    result_expires=3600,
)

pool = ConnectionPool(host=REDIS_HOST, port=int(REDIS_PORT), db=int(REDIS_DB),password=REDIS_PASSWORD)
class DatabaseTask(Task):
    def on_success(self, retval, task_id, args, kwargs):
        session = Session()
        try:
            task_result = session.get(File, kwargs["id"])
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
        session = Session()
        try:
            task_result = session.get(File, kwargs["id"])
            if task_result is not None:
                task_result.status = "FAILURE"
                session.commit()
        except Exception as e:
            session.rollback()
            raise
        finally:
            Session.close()


@celery_app.task(bind=True, base=DatabaseTask)
def ASR_predict(self,id,file, prompt,api_key,access_token,key_api_key,key_access_token):
    pass


@celery_app.task(bind=True, base=DatabaseTask)
def OCR_predict(self,id,file, prompt,api_key,access_token,key_api_key,key_access_token):
    pass

@celery_app.task(bind=True, base=DatabaseTask)
def OCR_predict_Text(self,id,content, prompt,api_key,access_token,key_api_key,key_access_token):
    pass
@celery_app.task(bind=True, base=DatabaseTask)
def NLP_edit_OCR(self,id,content, prompt,api_key,access_token,key_api_key,key_access_token):
    pass



@celery_app.task(bind=True, base=DatabaseTask)
def NLP_edit_ASR(self,id,content, prompt,api_key,access_token,key_api_key,key_access_token):
    pass


@celery_app.task(bind=True)
def Mail_sent(self,mail):
    pass