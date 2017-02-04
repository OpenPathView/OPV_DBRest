from flask import Flask

app = Flask('DBrest')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
