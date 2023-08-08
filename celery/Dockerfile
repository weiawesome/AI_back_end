FROM python:3.9-slim-buster

#RUN apt-get update && apt-get install -y \
#    python3-pip \
#    python3-dev

RUN adduser --disabled-password --gecos '' celery_user
WORKDIR /celery

COPY requirements.txt .

#RUN pip install --no-cache-dir -r requirements.txt
#RUN #apt-get update && apt-get install -y ffmpeg
#RUN pip3 install torch --index-url https://download.pytorch.org/whl/cu118
#RUN pip3 install torchaudio --index-url https://download.pytorch.org/whl/cu118
RUN pip install sqlalchemy celery[redis]

COPY . .
USER celery_user

CMD ["celery", "-A", "tasks", "worker","--loglevel=info","-c","5"]