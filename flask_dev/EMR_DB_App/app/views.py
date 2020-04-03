from flask_sqlalchemy import SQLAlchemy
from app import app, db

class Noteevents(db.Model):
    row_id = db.Column(db.Integer, primary_key=True, nullable=False)
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
    admissions = db.relationship('Admissions', backref='noteevents', lazy=True)

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

class Diagnoses_icd(db.Model):
    row_id = db.Column(db.Integer, primary_key=True)
    subject_id = db.Column(db.Integer, nullable=False)
    hadm_id = db.Column(db.Integer, nullable=False)
    seq_num = db.Column(db.Integer, nullable=False)
    icd9_code = db.Column(db.VARCHAR(length=10))

@app.route('/health')
def health_check():
    return 'OK. APIs are running.'

@app.route('/noteevents')
def get_notes():
    notes = Noteevents.query\
            .join(Admissions, Noteevents.hadm_id==Admissions.hadm_id)\
            .add_columns(
                    Noteevents.row_id,
                    Noteevents.text,
                    Noteevents.subject_id,
                    Noteevents.hadm_id,
                    Admissions.admittime,
                    Admissions.dischtime,
                    Admissions.deathtime)\
            .all()
    json_notes=[]
    for note in notes:
        json_note = {
                        'row_id':note.row_id,
                        'text':note.text,
                        'admittime':note.admittime,
                        'dischtime':note.dischtime,
                        'deathtime':note.deathtime,
                        'patient_id': note.subject_id,
                        'admission_id': note.hadm_id
                        }
        json_notes.append(json_note)
    return {'json_notes':json_notes}

@app.route('/noteevents/admitid/<admit_id>')
def get_notes_from_admit_id(admit_id):
    notes = Noteevents.query.filter_by(hadm_id=admit_id).all()
    json_notes = []
    for note in notes:
        json_note = {'note': note.text}
        json_notes.append(json_note)
    return {'json_notes':json_notes}

@app.route('/icd9/admitid/<admit_id>')
def get_icd_codes_from_admit_id(admit_id):
    codes = Diagnoses_icd.query.filter_by(hadm_id=admit_id).all()
    json_codes = []
    for code in codes:
        json_code = {'code': code.icd9_code}
        json_codes.append(json_code)
    return {'json_codes':json_codes}
    return admit_id

@app.route('/noteevents/page/<page>')
def get_notes_page(page):

    notes = Noteevents.query.join(Admissions,Noteevents.hadm_id==Admissions.hadm_id).add_columns(
            Noteevents.row_id,
            Noteevents.text,
            Noteevents.subject_id,
            Noteevents.hadm_id,
            Admissions.admittime,
            Admissions.dischtime,
            Admissions.deathtime,
            Admissions.insurance,
            Admissions.language,
            Admissions.religion,
            Admissions.marital_status,
            Admissions.ethnicity,
            Admissions.diagnosis).paginate(int(page),100000)
    json_notes = []
    for item in notes.items:
        note = {'row_id': item.row_id,
                'text': item.text,
                'admittime': item.admittime,
                'dischtime': item.dischtime,
                'deathtime': item.deathtime,
                'patient_id': item.subject_id,
                'admission_id': item.hadm_id,
                'insurance': item.insurance,
                'language': item.language,
                'religion': item.religion,
                'marital_status': item.marital_status,
                'ethnicity': item.ethnicity,
                'diagnosis': item.diagnosis
                }
        json_notes.append(note)
    return {'json_notes':json_notes}

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

@app.route('/admissions')
def get_admissions():
    admissions_query = Admissions.query.all()
    admissions = []
    for entry in admissions_query:
        admission = {
                'admission_id':entry.hadm_id, 
                'admittime': entry.admittime, 
                'dischtime': entry.dischtime, 
                'deathtime': entry.deathtime, 
                'patient_id': entry.subject_id,
                'insurance': entry.insurance,
                'language': entry.language,
                'religion': entry.religion,
                'marital_status': entry.marital_status,
                'ethnicity': entry.ethnicity,
                'diagnosis': entry.diagnosis,
                }
        admissions.append(admission)
    return {'json_admissions': admissions}

@app.route('/admissions/<size>')
def get_admissions_size(size):
    admissions_query = Admissions.query.limit(size).all()
    admissions = []
    for entry in admissions_query:
        admission = {'admission_id':entry.hadm_id, 'admittime': entry.admittime, 'dischtime': entry.dischtime, 'deathtime': entry.deathtime, 'patient_id': entry.subject_id}
        admissions.append(admission)
    return {'json_admissions': admissions}

@app.route('/noteevent/<note_id>')
def get_note(note_id):
    note = Noteevents.query.filter_by(row_id=note_id).first()
    return {'note': note.text}
  
@app.route('/noteeventsold')
def get_notes_old():
    notes = Noteevents.query.all()
    return {'notes': [note.text for note in notes]}

@app.route('/noteeventscount')
def get_notes_count():
    count = Noteevents.query\
            .join(Admissions,Noteevents.hadm_id==Admissions.hadm_id)\
            .add_columns(
                    Noteevents.row_id,
                    Noteevents.text,
                    Noteevents.subject_id,
                    Noteevents.hadm_id,
                    Admissions.admittime,
                    Admissions.dischtime,
                    Admissions.deathtime)\
            .count()
    return {'note_count':count}

@app.route('/icdcount')
def get_icd_count():
    count = Diagnoses_icd.query.count()
    return {'icd_count': count}

@app.route('/icdcodes')
def get_all_codes():
    codes = Diagnoses_icd.query.all()
    json_codes = []
    for code in codes:
        json_code = {
                'admission_id': code.hadm_id,
                'icd_code': code.icd9_code
            }
        json_codes.append(json_code)
    return {'json_codes': json_codes}


@app.route('/noteevents/<size>')
def get_notes_size(size):
    notes = Noteevents.query\
            .join(Admissions, Noteevents.hadm_id==Admissions.hadm_id)\
            .add_columns(
                    Noteevents.row_id, 
                    Noteevents.text,
                    Noteevents.subject_id,
                    Noteevents.hadm_id,
                    Admissions.admittime, 
                    Admissions.dischtime, 
                    Admissions.deathtime)\
            .limit(size).all()
    json_notes=[]
    for note in notes:
        json_note = {
                        'row_id':note.row_id,
                        'text':note.text, 
                        'admittime':note.admittime,
                        'dischtime':note.dischtime,
                        'deathtime':note.deathtime,
                        'patient_id': note.subject_id,
                        'admission_id': note.hadm_id

                    }
        json_notes.append(json_note)
    return {'json_notes':json_notes}
