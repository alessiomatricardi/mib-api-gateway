#
# Docker file for MessageInABottle S4 v1.0
#
FROM python:3.8
LABEL maintainer="4_squad"
LABEL version="1.0"
LABEL description="Message In a Bottle API Gateway"

# creating the environment
COPY . /app
# moving the static contents
RUN ["mv", "/app/mib/static", "/static"]
# setting the workdir
WORKDIR /app
# set timezone to Europe/Rome
ENV TZ=Europe/Rome

# installing all requirements
RUN ["pip", "install", "-r", "requirements.prod.txt"]

# exposing the port
EXPOSE 5000/tcp

# Main command
CMD ["gunicorn", "--config", "gunicorn.conf.py", "wsgi:app"]