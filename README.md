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
opv-api run --db-location="postgres://opv:opv@localhost/dev_rederbro" --rederbroID="TestID" --debug=True --port=5000
```

# How to set db ?
Via CLI parameters.
To display help :
```bash
opv-api -h
```
