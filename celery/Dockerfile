# 使用官方 Python 基礎映像檔作為基礎
FROM nvidia/cuda:12.0.0-cudnn8-devel-ubuntu22.04

RUN apt-get update && apt-get install -y \
    python3-pip \
    python3-dev
# 設置工作目錄
WORKDIR /celery

COPY requirements.txt .

# 安裝應用程式所需的依賴包
RUN pip install --no-cache-dir -r requirements.txt
RUN apt-get update && apt-get install -y ffmpeg
RUN pip3 install torch --index-url https://download.pytorch.org/whl/cu118
RUN pip3 install torchaudio --index-url https://download.pytorch.org/whl/cu118

# 將應用程式代碼複製到工作目錄
COPY . .

CMD ["celery", "-A", "tasks", "worker","--loglevel=info","-c","5"]