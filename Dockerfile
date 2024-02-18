FROM python:3.11-alpine

LABEL author="Apoorv Dwivedi <apoorvd14@gmail.com>"

WORKDIR /app

ENV PYTHONUNBUFFERED=1

COPY requirements.txt /
RUN pip install -U pip -r /requirements.txt

COPY spam_check.py ./

RUN chmod +x /app/spam_check.py

ENTRYPOINT ["/app/spam_check.py"]
