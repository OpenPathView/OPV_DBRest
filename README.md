# Dependances
If you use postgresql you need to get
- libpq-dev 
- python3-dev

With apt: `sudo apt-get install libpq-dev python3-dev`

# How to run ?
Install the dbrest  
`hug -m dbrest.api` 
The server is running on :8000 (see hug options to set port, host...)

# How to set db ?
see dbrest/setting.py
