FROM nvidia/cuda:10.2-cudnn7-devel

RUN apt-get update -y
RUN apt-get install -y python3-pip python-dev build-essential

RUN apt-get install -y tesseract-ocr
RUN apt-get install -y tesseract-ocr-eng
RUN apt-get install -y tesseract-ocr-rus
RUN apt-get install -y libtesseract-dev

ENV LC_CTYPE=C.UTF-8

COPY ./requirements.txt $PROJECT_ROOT/
RUN pip3 install --upgrade pip

RUN pip3 install --no-cache-dir -r requirements.txt

CMD ["/bin/bash"]