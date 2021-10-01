# Example build command:
#
#    docker build -t osd2f-generic .
#  
# Example running command:
#
#    docker run \
#      -p 8000:8000 \
#      -e OSD2F_DB_URL='sqlite://:memory:' 
#      -e OSD2F_SECRET=secret 
#      osd2f-generic
#
FROM python:3.8.0-buster

EXPOSE 8000

ENV OSD2F_MODE=Production

# make code available
COPY ./ ./osd2f

# add build-secret to hypercorn config

WORKDIR /osd2f

# setup dependencies
RUN pip install ./ 
RUN pip install -r requirements.txt
RUN pip install -r requirements_dev.txt

# run tests
RUN flake8 ./
RUN mypy ./osd2f/ --ignore-missing-imports
RUN pytest ./
RUN osd2f --dry-run

# set the default command for the container (i.e. running production)
CMD [ "hypercorn", "osd2f.__main__:app", "-b", "0.0.0.0:8000"]
