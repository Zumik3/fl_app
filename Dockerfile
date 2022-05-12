FROM tiangolo/uwsgi-nginx-flask:python3.8

EXPOSE 5000

RUN pip install --upgrade pip

#RUN pip install peewee
#RUN pip install pymysql
#RUN pip install mysql-connector-python

COPY ./app /app
COPY requirements.txt /app/requirements.txt

WORKDIR /app
RUN pip install --no-cache-dir -r /app/requirements.txt

# Support tools
#RUN apt-get update
#RUN apt-get install -y mc