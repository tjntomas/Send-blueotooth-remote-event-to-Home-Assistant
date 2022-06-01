FROM python:3.10.0b1-buster
COPY code /app
WORKDIR /app 
RUN pip install -r reqs.txt
CMD python /app/ev_docker.py
