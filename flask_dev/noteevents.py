from flask import Flask
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://emrm1:emrm1@localhost:5432/mimic?options=-csearch_path=mimiciii,public'
db = SQLAlchemy(app)

class Noteevents(db.Model):
    row_id = db.Column(db.Integer, primary_key=True)
    subject_id = db.Column(db.Integer, nullable=False)
    hadm_id = db.Column(db.Integer)
    chartdate = db.Column(db.TIMESTAMP())
    charttime = db.Column(db.TIMESTAMP())
    storetime = db.Column(db.TIMESTAMP())
    category = db.Column(db.VARCHAR(length=50))
    description = db.Column(db.VARCHAR(length=255))
    cgid = db.Column(db.Integer)
    iserror = db.Column(db.CHAR(length=1))
    text = db.Column(db.TEXT())

@app.route('/')
def hello_world():
    return 'Hello, World!'

@app.route('/noteevents')
def get_notes():
    #engine=create_engine('postgresql://emrm1:emrm1@localhost:5432/mimic',connect_args={'options': '-csearch_path={}'.format('mimiciii,public')})
    #engine=create_engine('postgresql://emrm1:emrm1@localhost:5432/mimic?options=-csearch_path=mimiciii,public')
    #metadata = db.MetaData()
    #metadata.reflect(engine)
    #connection = engine.connect()
    #note_events = db.Table('noteevents', metadata, autoload=True, autoload_with=engine)
    #query = db.select([note_events])
    #ResultProxy=connection.execute(query)
    #ResultSet=ResultProxy.fetchall()
    notes = Noteevents.query.all()
    return {'notes': [note.text for note in notes]}

@app.route('/noteevent/<note_id>')
def get_note(note_id):
    engine=create_engine('postgresql://emrm1:emrm1@localhost:5432/mimic',connect_args={'options': '-csearch_path={}'.format('mimiciii,public')})
    metadata = db.MetaData()
    metadata.reflect(engine)
    connection = engine.connect()
    note_events = db.Table('noteevents', metadata, autoload=True, autoload_with=engine)
    query = db.select([note_events]).where(note_events.columns.row_id==note_id)
    ResultProxy=connection.execute(query)
    ResultSet=ResultProxy.fetchall()
    return {'notes':[dict(row) for row in ResultSet]}
   
@app.route('/noteevents/<size>')
def get_notes_size(size):
    notes = Noteevents.query.limit(size).all()
    return {'notes':[note.text for note in notes]}
