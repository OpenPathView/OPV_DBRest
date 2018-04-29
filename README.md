# Dependencies
If you use postgresql you need to get
- libpq-dev
- python3-dev

With apt: `sudo apt-get install libpq-dev python3-dev`

# Install it
```bash
python setup.py install
```

# How to run ?
Install the dbrest  
```bash
opv-api run --db-location="postgres://opv:opv@localhost/dev_rederbro" --IDMalette="TestID" --debug=True --port=5000
```

# How to set db ?
Via CLI parameters.
To display help :
```bash
opv-api -h
```

# How to export datas
You can export partial data from the dabase with all their dependencies. Use the command `òpv-db-export`.
See the CLI documentation `òpv-db-export -h` and the following explanation.

## Exported tables
To use this command you need to know what table you want to export (2nd parameter), the script will automatically
export all needed tables so that the exported tables have the foreign ones. For instance when you export 'panorama'
table the script

## Filters
To select partial datas you will need to define a filter (otherwise it will export the entire database). The filter is
simply an SQL select statement with 'table_name.col = value'.

Here is an exemple to select all datas in the area [(lon:48.3993, lat:-4.472865) and (lon:48.399398, lat:-4.472867)], from campaign 1 of malette 2.
```SQL
campaign.id_campaign = 1 AND campaign.id_malette = 2 AND s.gps_pos && ST_MakeEnvelope(48.3993, -4.472865, 48.399398, -4.472867, 4326);
```

## Directory Manager files
Exporting the database whithout the files referenced in it and stored in the directory manager might be useless, but sometimes you don't want
to export all files, to list the directory UUIDs you want to export list the concerned columns (where they are specified) using the option
`--dm-cols`. For instance to get all equirectangular directory UUIDs and image sets UUIDs use `panorama.equirectangular_path,lot.pictures_path`.

This will output all directories UUID in a plain text file, one ID per line so that you can reuse them to make an archive or rsync. For instance to make
an archive from the output list of dm uuids, go to your Directory Manager data folder and run :
```bash
# Inside the directory manager data folder
tar -zcvf /tmp/dm_archive.tar.gz -T /tmp/dms.txt
```

## Exemple

For instance to export all panorama of campaign 2 in the view box (), with the directory UUIDs list of the equirectangular files :
```bash
opv-db-export "postgres://opv:pwd@locahost/opv" "panorama" --filters="campaign.id_campaign=85" --output-dm-list-file="/tmp/dms.txt" --output-sql="/tmp/export_dump.sql" --dm-cols="panorama.equirectangular_path,lot.pictures_path" --debug
# Make an archive with directory manager uuids
# go to your directory manager folder
tar -zcvf /tmp/dm_archive.tar.gz -T /tmp/dms.txt
# Importing - data back, you should be logged in as postgres user
PGPASSWORD=pwd psql -U opv opv < /tmp/export_dump.sql
# For directory manager simplfy uncompress it in the correct folder
```

# Migrate or update your existing database
To migrate or update your existing database to the latest model/schema version simply run :
```bash
opv-db-migrate --db-uri="postgres://USER:PWD@HOST/DB"
```
You should run this script after each code update.

# Commit change on datbase model
The database model is versionned using sqlalchemy-migrate module.
Before making any change make sure you have a running database with the latest version of the model, launch `opv-db-migrate` before making any change.
When you change `model.py` you need to commit your changes using the following command line :
```bash
dbrest/database/commit_db_model.py "my commit description" --db-uri="postgres://USER:PWD@HOST/DB"
```
This script will version you change and upgrade the database.
