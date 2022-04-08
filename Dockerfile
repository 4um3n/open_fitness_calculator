FROM python:3
ENV PYTHONBUFFERED=1
WORKDIR /app
COPY ./requirements.txt /app/
RUN pip3 install -r requirements.txt
COPY . /app/
