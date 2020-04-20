from flask import Flask
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://emrm1:emrm1@10.32.22.6:5432/mimic?options=-csearch_path=mimiciii,public'
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
    hadm_id = db.Column(db.Integer,db.ForeignKey('noteevents.hadm_id'), nullable=False)

class Admissions(db.Model):
    row_id = db.Column(db.Integer, primary_key=True)
    subject_id = db.Column(db.Integer, nullable=False)
    hadm_id = db.Column(db.Integer,db.ForeignKey('noteevents.hadm_id'), nullable=False)
    admittime = db.Column(db.TIMESTAMP(), nullable=False)
    dischtime = db.Column(db.TIMESTAMP(), nullable=False)
    deathtime = db.Column(db.TIMESTAMP())
    admission_location = db.Column(db.VARCHAR(length=50), nullable=False)
    discharge_location = db.Column(db.VARCHAR(length=50), nullable=False)
    insurance = db.Column(db.VARCHAR(length=255), nullable=False)
    language = db.Column(db.VARCHAR(length=10))
    religion = db.Column(db.VARCHAR(length=50))
    marital_status = db.Column(db.VARCHAR(length=50))
    ethnicity = db.Column(db.VARCHAR(length=200), nullable=False)
    edregtime = db.Column(db.TIMESTAMP())
    edouttime = db.Column(db.TIMESTAMP())
    diagnosis = db.Column(db.VARCHAR(length=255))
    hospital_expire_flag = db.Column(db.SmallInteger)
    has_chartevents_data = db.Column(db.SmallInteger,nullable=False)

class Patients(db.Model):
    row_id = db.Column(db.Integer, primary_key=True)
    subject_id = db.Column(db.Integer)
    gender = db.Column(db.VARCHAR(5))
    dob = db.Column(db.TIMESTAMP())
    dod = db.Column(db.TIMESTAMP())
    dod_hosp = db.Column(db.TIMESTAMP())
    dod_ssn = db.Column(db.TIMESTAMP())
    expire_flag = db.Column(db.VARCHAR(5))

@app.route('/')
def hello_world():
    return 'Hello, World!'

@app.route('/patient/<size>')
def get_patients_size(size):
    patients_query = Patients.query.limit(size).all()
    json_patients = []
    for patient in patients_query:
        json_patient = {
                            'row_id': patient.row_id,
                            'patient_id': patient.subject_id,
                            'gender': patient.gender,
                            'dob': patient.dob
                }
        json_patients.append(json_patient)
    return {'json_patients':json_patients}

@app.route('/patients')
def get_patients():
    patients_query = Patients.query.all()
    json_patients = []
    for patient in patients_query:
        json_patient = {
                        'row_id': patient.row_id,
                        'patient_id': patient.subject_id,
                        'gender': patient.gender,
                        'dob': patient.dob
                       }
        json_patients.append(json_patient)
    return {'json_patients':json_patients}

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

@app.route('/noteevents/page/<page>')
def get_notes_page(page):
    notes = Noteevents.query.join(Admissions,Noteevents.hadm_id==Admissions.hadm_id).add_columns(Noteevents.row_id,Noteevents.text,Noteevents.subject_id,Noteevents.hadm_id,Admissions.admittime,Admissions.dischtime,Admissions.deathtime).paginate(int(page),100000)
    json_notes = []
    for item in notes.items:
        note = {'row_id': item.row_id,'text': item.text,'admittime': item.admittime,'dischtime': item.dischtime,'deathtime': item.deathtime,'patient_id': item.subject_id,'admission_id': item.hadm_id}
        json_notes.append(note)
    return {'json_notes':json_notes}

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

@app.route('/admissions/los/page/<page>')
def get_los(page):
   #admissions = Admissions.query.add_columns(Admissions.row_id, Admissions.admittime, Admissions.dischtime).paginate(int(page),100000)
    admissions = Noteevents.query.join(Admissions,Noteevents.hadm_id==Admissions.hadm_id).add_columns(Noteevents.row_id,Noteevents.hadm_id,Admissions.admittime,Admissions.dischtime,Admissions.deathtime).paginate(int(page),100000)
    json_admissions = []
    for item in admissions.items:
        los = item.dischtime - item.admittime
        json_los = {'days': los.days, 'seconds': los.seconds}
        admission = {'row_id':item.row_id, 'admission_id': item.hadm_id, 'admittime': item.admittime, 'dischtime': item.dischtime, 'los': json_los}
        json_admissions.append(admission)
    return{'json_admissions': json_admissions}
