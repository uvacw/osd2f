FROM python:3.9.0-buster
ARG secret
ENV OSD2F_SECRET=$secret
ENV PYTHONUNBUFFERED 1
ENV DOCKER_CONTAINER 1
RUN apt-get update && apt-get install -y python-dev sqlite3

# make code available
RUN mkdir /osd2f
COPY . /osd2f

# setup dependencies
RUN pip install --upgrade pip
RUN pip install ./osd2f
RUN pip install  -r osd2f/requirements/local.txt #--no-cache-dir

COPY ./DockerCompose/python/hypercorn.sh /hypercorn.sh
RUN sed -i 's/\r//' /hypercorn.sh
RUN chmod +x /hypercorn.sh

WORKDIR /osd2f

# run tests uncomment to have them run
#RUN flake8 ./
#RUN mypy ./osd2f/ --ignore-missing-imports
#RUN pytest ./


# set the default command for the container (i.e. running production) but for local this is set within the hypercorn.sh file
# This is done in docker-compose