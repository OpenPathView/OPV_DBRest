#!/bin/bash


until PGPASSWORD=${OPV_DBREST_PASSWORD} psql -h "${OPV_DBREST_USER}" -U "postgres" -c '\q'; do
  >&2 echo "Postgres is unavailable - sleeping"
  sleep 1
done

opv-db-migrate --db-uri="postgres://${OPV_DBREST_USER}:${OPV_DBREST_PASSWORD}@${OPV_DBREST_DB_ADDRESS}/${OPV_DBREST_DB}" 

opv-api run --db-location="postgres://${OPV_DBREST_USER}:${OPV_DBREST_PASSWORD}@${OPV_DBREST_DB_ADDRESS}/${OPV_DBREST_DB}" --IDMalette="${OPV_DBREST_ID_MALETTE}" --debug=${OPV_DBREST_DEBUG} --port=${OPV_DBREST_PORT}
