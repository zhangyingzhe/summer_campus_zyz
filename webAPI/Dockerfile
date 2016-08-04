FROM ubuntu:latest

RUN apt-get update -y
RUN apt-get install -y python-pip python-dev build-essential
RUN pip install watson-developer-cloud
RUN pip install cassandra-driver
ADD 
COPY . /app
WORKDIR /app
RUN pip install -r requirements.txt
ADD trans.txt /app
ADD analyze.txt /app
ADD 11.png /app
ENTRYPOINT ["python"]
CMD ["app.py"]
