FROM python:3.9-slim-buster
WORKDIR /app
COPY requirements.txt requirements.txt
RUN pip3 install -r requirements.txt
COPY .. .
# 啟動應用程式
CMD ["gunicorn", "--bind", "0.0.0.0:8080", "main:app"]