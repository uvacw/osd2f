FROM python:3.8.12-buster

EXPOSE 8000

ENV OSD2F_SECRET=""
ENV OSD2F_MODE="Development"
ENV OSD2F_DB_URL="sqlite://:memory:"

# make code available
COPY ./ ./osd2f

# add build-secret to hypercorn config

WORKDIR /osd2f

# setup dependencies
RUN pip install ./ 

# minimal check to make sure the install works
RUN osd2f --dry-run

# set the default command for the container (i.e. running production)
CMD [ "hypercorn", "osd2f.__main__:app", "-b", "0.0.0.0:8000" ]
