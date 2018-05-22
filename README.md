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

# Migrate or update your existing database
To migrate or update your existing database to the latest model/schema version simply run :
```bash
opv-db-migrate --db-uri="postgres://USER:PWD@HOST/DB"
```
You should run this script after each code update.

# Commit change on database model
The database model is versionned using sqlalchemy-migrate module.
Before making any change make sure you have a running database with the latest version of the model, launch `opv-db-migrate` before making any change.
When you change `model.py` you need to commit your changes using the following command line :
```bash
dbrest/database/commit_db_model.py "my commit description" --db-uri="postgres://USER:PWD@HOST/DB"
```
This script will version you change and upgrade the database.
