FROM python:3.6

WORKDIR /

COPY requirements.txt requirements.txt
COPY worker.py worker.py

RUN pip install -r requirements.txt

CMD ["python", "worker.py"]