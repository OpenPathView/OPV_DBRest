FROM python:3.6

RUN apt-get update && apt-get install -y libpq-dev python3-dev && rm -rf /var/lib/apt/lists/*

ENV OPV_DBREST_ID_MALETTE 42
ENV OPV_DBREST_PORT 5000
ENV OPV_DBREST_DEBUG False
ENV OPV_DBREST_USER opv
ENV OPV_DBREST_PASSWORD opv42
ENV OPV_DBREST_DB opv
ENV OPV_DBREST_DB_ADDRESS postgres

COPY . /source/DBRest

WORKDIR /source/DBRest

RUN pip3 install -r requirements.txt && \
python3 setup.py install

EXPOSE ${OPV_DBREST_PORT}:${OPV_DBREST_PORT}

CMD ["opv-api", "run", "--db-location=\"postgres://${OPV_DBREST_USER}:${OPV_DBREST_PASSWORD}@${OPV_DBREST_DB_ADDRESS}/${OPV_DBREST_DB}\"", "--IDMalette=\"${OPV_DBREST_ID_MALETTE}\"", "--debug=${OPV_DBREST_DEBUG}", "--port=${OPV_DBREST_PORT}"]

