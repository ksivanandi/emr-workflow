from flask import Flask
from flask_sqlalchemy import SQLAlchemy
app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://emrm1:emrm1@10.32.23.1:5432/mimic?options=-csearch_path=mimiciii,public'
db = SQLAlchemy(app)
from app import views
