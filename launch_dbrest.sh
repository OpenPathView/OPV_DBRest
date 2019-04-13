#!/bin/bash

opv-db-migrate --db-uri="postgres://${OPV_DBREST_USER}:${OPV_DBREST_PASSWORD}@${OPV_DBREST_DB_ADDRESS}/${OPV_DBREST_DB}" 

opv-api run --db-location="postgres://${OPV_DBREST_USER}:${OPV_DBREST_PASSWORD}@${OPV_DBREST_DB_ADDRESS}/${OPV_DBREST_DB}" --IDMalette="${OPV_DBREST_ID_MALETTE}" --debug=${OPV_DBREST_DEBUG} --port=${OPV_DBREST_PORT}
