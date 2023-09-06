FROM python:3.10-alpine
ENV PYTHONUNBUFFERED 1
WORKDIR /nextnode
COPY requirements.txt requirements.txt
RUN pip3 install -r requirements.txt
COPY . .