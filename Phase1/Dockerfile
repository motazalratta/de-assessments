FROM python:3.8-slim-buster

COPY ./requirements.txt /tmp/requirements.txt

WORKDIR /app

RUN pip3 install -r /tmp/requirements.txt

COPY ./app ${WORKDIR}

ENV GOOGLE_APPLICATION_CREDENTIALS ="${WORKDIR}/config/googlecloud.key.file.json"
ENV GOOGLE_CLOUD_PROJECT = ""

CMD [ "python3", "main.py" ,"--schema", "configschema.json", "--ymlfile", "config/config.yml" ]