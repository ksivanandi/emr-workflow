# more /conda/envs/rapids/lib/python3.6/site-packages/medacy/pipeline_components/units/unit_component.py

from spacy.tokens import Token
from spacy.matcher import Matcher
from spacy.matcher import PhraseMatcher
from spacy.tokens import Span
#from ..base import BaseComponent
from jason_base_component import BaseComponent

import logging

import re

class UnitComponent(BaseComponent):
    """
    A pipeline component that tags units.
    Begins by first tagging all mass, volume, time, and form units then aggregates as necessary.
    """

    name="unit_annotator"
    dependencies = []

    def __init__(self, nlp):
        self.nlp = nlp
        self.nlp_priv = nlp
        
        s = Extract_Med_Features()

        
        #Token.set_extension('feature_is_record_id', default=False)
        Token.set_extension('feature_is_record_id', default=False, force=True)
        nlp.entity.add_label('record_id')
        
        Token.set_extension('feature_is_mass_unit', default=False, force=True)
        nlp.entity.add_label('mass_unit')

        Token.set_extension('feature_is_volume_unit', default=False, force=True)
        nlp.entity.add_label('volume_unit')

        Token.set_extension('feature_is_time_unit', default=False, force=True)
        nlp.entity.add_label('time_unit')

        Token.set_extension('feature_is_route_type', default=False, force=True)
        nlp.entity.add_label('route_type')

        Token.set_extension('feature_is_form_unit', default=False, force=True)
        nlp.entity.add_label('form_unit')

        Token.set_extension('feature_is_frequency_indicator', default=False, force=True)
        nlp.entity.add_label('frequency_indicator')


        Token.set_extension('feature_is_measurement_unit', default=False, force=True)
        nlp.entity.add_label('measurement_unit')

        Token.set_extension('feature_is_measurement', default=False, force=True)
        nlp.entity.add_label('measurement')

        #Token.set_extension('feature_is_duration_pattern', default=False)
        Token.set_extension('feature_is_duration_pattern', default=False, force=True)
        nlp.entity.add_label('duration_pattern')

        #Token.set_extension('feature_is_clock', default=False)
        Token.set_extension('feature_is_clock', default=False, force=True)
        nlp.entity.add_label('clock')

        #Token.set_extension('feature_is_drug', default=False)
        Token.set_extension('feature_is_drug', default=False, force=True)
        nlp.entity.add_label('drug')
        
        #Token.set_extension('feature_is_diagnosis', default=False)
        Token.set_extension('feature_is_diagnosis', default=False, force=True)
        nlp.entity.add_label('diagnosis')
        
        #Token.set_extension('feature_is_admission_date', default=False)
        Token.set_extension('feature_is_admission_date', default=False, force=True)
        nlp.entity.add_label('admission_date')
        
        #Token.set_extension('feature_is_discharge_date', default=False)
        Token.set_extension('feature_is_discharge_date', default=False, force=True)
        nlp.entity.add_label('discharge_date')
        
        #Token.set_extension('feature_is_temperature', default=False)
        Token.set_extension('feature_is_temperature', default=False, force=True)
        nlp.entity.add_label('temperature')
        
        #Token.set_extension('feature_is_blood_pressure', default=False)
        Token.set_extension('feature_is_blood_pressure', default=False, force=True)
        nlp.entity.add_label('blood_pressure')
        
        self.record_id_matcher = Matcher(nlp.vocab)
        self.mass_matcher = Matcher(nlp.vocab)
        self.volume_matcher = Matcher(nlp.vocab)
        self.time_matcher = Matcher(nlp.vocab)
        self.route_matcher = Matcher(nlp.vocab)
        self.form_matcher = Matcher(nlp.vocab)
        self.unit_of_measurement_matcher = Matcher(nlp.vocab)
        self.measurement_matcher = Matcher(nlp.vocab)
        self.frequency_matcher = Matcher(nlp.vocab)
        self.duration_matcher = Matcher(nlp.vocab)
        self.clock_matcher = Matcher(nlp.vocab)
        self.drug_matcher = PhraseMatcher(nlp.vocab, attr='LOWER')
        self.diagnosis_matcher = PhraseMatcher(nlp.vocab, attr='LOWER')
        self.admission_date_matcher = Matcher(nlp.vocab)
        self.discharge_date_matcher = Matcher(nlp.vocab)
        self.temperature_matcher = Matcher(nlp.vocab)
        self.blood_pressure_matcher = Matcher(nlp.vocab)
        self.record_id_matcher = Matcher(nlp.vocab)
        
        
        #self.record_id_matcher.add('RECORD_ID', None,
        #                          [{"IS_PUNCT": True}, {"IS_DIGIT": True}, {"IS_UPPER": True}, {"IS_DIGIT": True}, {"IS_DIGIT": True}]
        #                          )
        
        self.record_id_matcher.add('RECORD_ID', None,
                                  [{'ORTH': 'RECORD'}]
                                  )
        
        self.mass_matcher.add('UNIT_OF_MASS', None,
                              [{'LOWER': 'mcg'}],
                              [{'LOWER': 'microgram'}],
                              [{'LOWER': 'micrograms'}],
                              [{'ORTH': 'mg'}],
                              [{'LOWER': 'milligram'}],
                              [{'LOWER': 'g'}],
                              [{'LOWER': 'kg'}],
                              [{'ORTH': 'mEq'}]
                             )

        self.volume_matcher.add('UNIT_OF_VOLUME', None,
                                [{'LOWER': 'ml'}],
                                 [{'ORTH': 'dL'}],
                                [{'LOWER': 'cc'}],
                                [{'ORTH': 'L'}]
                               )

        self.time_matcher.add('UNIT_OF_TIME', None,
                              [{'LOWER': 'sec'}],
                              [{'LOWER': 'second'}],
                              [{'LOWER': 'seconds'}],
                              [{'LOWER': 'min'}],
                              [{'LOWER': 'minute'}],
                              [{'LOWER': 'minutes'}],
                              [{'LOWER': 'hr'}],
                              [{'LOWER': 'hour'}],
                              [{'LOWER': 'day'}],
                              [{'LOWER': 'days'}],
                              [{'LOWER': 'week'}],
                              [{'LOWER': 'weeks'}],
                              [{'LOWER': 'month'}],
                              [{'LOWER': 'months'}],
                              [{'LOWER': 'year'}],
                              [{'LOWER': 'years'}],
                              [{'LOWER': 'yrs'}]
                             )

        self.frequency_matcher.add('FREQUENCY_MATCHER', None,
                               [{'LOWER': 'bid'}],
                               [{'LOWER': 'b.i.d'}, {"IS_PUNCT": True}],
                               [{'LOWER': 'prn'}],
                               [{'LOWER': 'qid'}],
                               [{'LOWER': 'tid'}],
                               [{'LOWER': 'qd'}],
                               [{'LOWER': 'q.d'}, {"IS_PUNCT": True}],
                               [{'LOWER': 'q'}, {'LOWER': 'd'}],
                               [{'LOWER': 'q'}, {'LOWER': 'daily'}],
                               [{'LOWER': 'daily'}],
                               [{'LOWER': 'nightly'}],   
                               [{'LOWER': 'hs'}],
                               [{'LOWER': 'as'}, {'LOWER': 'needed'}],
                               [{'LOWER': 'once'}, {'LOWER': 'a'}, {'LOWER': 'day'}],
                               [{'LOWER': 'twice'}, {'LOWER': 'a'}, {'LOWER': 'day'}]
                                  )


        self.form_matcher.add('UNIT_OF_FORM', None,
                              [{'ORTH': 'dose'}],
                              [{'ORTH': 'doses'}],
                              [{'LEMMA': 'pill'}],
                              [{'LEMMA': 'tablet'}],
                              [{'LEMMA': 'unit'}],
                              [{'LEMMA': 'u'}],
                              [{'LEMMA': 'patch'}],
                              [{'LEMMA': 'unit'}],
                              [{'ORTH': 'lotion'}],
                              [{'ORTH': 'powder'}],
                              [{'ORTH': 'amps'}],
                              [{'LOWER': 'actuation'}],
                              [{'LEMMA': 'suspension'}],
                              [{'LEMMA': 'syringe'}],
                              [{'LEMMA': 'puff'}],
                              [{'LEMMA': 'liquid'}],
                              [{'LEMMA': 'aerosol'}],
                              [{'LEMMA': 'cap'}]
                             )

        self.route_matcher.add('TYPE_OF_ROUTE', None,
                               [{'LOWER': 'IV'}],
                               [{'ORTH': 'intravenous'}],
                               [{'ORTH': 'gtt'}],
                               [{'LOWER': 'drip'}],
                               [{'LOWER': 'inhalation'}],
                               [{'LOWER': 'by'}, {'LOWER': 'mouth'}],
                               [{'LOWER': 'topical'}],
                               [{'LOWER': 'subcutaneous'}],
                               [{'LOWER': 'ophthalmic'}],
                               [{'LEMMA': 'injection'}],
                               [{'LOWER': 'mucous'}, {'LOWER': 'membrane'}],
                               [{'LOWER': 'oral'}],
                               [{'LOWER': 'nebs'}],
                               [{'LOWER': 'transdermal'}],
                               [{'LOWER': 'nasal'}],
                               [{'LOWER': 'po'}],
                               [{'LOWER': 'p.o'}, {"IS_PUNCT": True}]
                              )


        self.unit_of_measurement_matcher.add('UNIT_OF_MEASUREMENT', None,
                         [{'ENT_TYPE': 'mass_unit'}, {'ORTH': '/'}, {'ENT_TYPE': 'volume_unit'}],
                         [{'ENT_TYPE': 'volume_unit'}, {'ORTH': '/'}, {'ENT_TYPE': 'time_unit'}],
                         [{'ENT_TYPE': 'form_unit'}, {'ORTH': '/'}, {'ENT_TYPE': 'volume_unit'}]
                                            )
        self.measurement_matcher.add('MEASUREMENT', None,
                         [{'LIKE_NUM': True}, {'ORTH': '%'}],
                         [{'LIKE_NUM': True}, {'ENT_TYPE': 'measurement_unit'}],
                         [{'LIKE_NUM': True}, {'ENT_TYPE': 'mass_unit'}],
                         [{'LIKE_NUM': True}, {'ENT_TYPE': 'volume_unit'}],
                         [{'LIKE_NUM': True}, {'ENT_TYPE': 'form_unit'}],
                         [{'LIKE_NUM': True},{'LOWER': 'x'}, {'ENT_TYPE': 'form_unit'}]
                                    )

        self.duration_matcher.add('DURATION', None,
                                  [{'POS': 'PREP'}, {'LIKE_NUM': True}, {'ENT_TYPE': 'time_unit'}],
                                  [{'LOWER': 'in'}, {'LIKE_NUM': True},{'ENT_TYPE': 'time_unit'}],
                                  [{'LIKE_NUM': True}, {'ENT_TYPE': 'time_unit'}],
                                  [{'LOWER': 'prn'}]
                                 )

        self.clock_matcher.add('CLOCK', None,
                                  [{"TEXT": {'REGEX': '[0-1]?[0-9]/[0-1]?[0-9]/[1-2]?[0-9]?[0-9][0-9]'}}, {"TEXT": {'REGEX': '[0-1]?[0-9]:[0-5]?[0-9]:[0-5]?[0-9]'}}, {'LOWER': {'REGEX': 'am|pm'}}]
                              )
        
        
        #self.drug_matcher.add("DRUG", None, self.nlp_priv(u"LOVENOX"))#Lovenox
        #self.drug_matcher.add("DRUG", None, self.nlp_priv(u"ZOCOR"))
        #self.drug_matcher.add("DRUG", None, self.nlp_priv(u"LAMICTAL"))
        
        f = open("/home/amalinow/andrew-rapids/Jason's Sandbox/_drug_list.txt", "rt")
        content_lines=f.readlines()
        f.close()
        
        for str in content_lines:
            str1=str.lstrip('1234567890, ')
            str2=str1.split(',')
            
            for item in str2:
                item_10=item.strip() #remove "'.
                item_1=item_10.strip('"')
                self.drug_matcher.add("DRUG", None, self.nlp_priv(item_1))
                
                
        #self.diagnosis_matcher.add("DIAGNOSIS", None, self.nlp_priv(u"Chronic kidney disease"))
        
        #f = open("/rapids/notebooks/hostfs/Jason's Sandbox/_AZ_00 Diagnosis list.txt", "rt")
        f = open("/home/amalinow/andrew-rapids/Jason's Sandbox/icd10cm_codes one-clean.txt", "rt")
        content_lines=f.readlines()
        f.close()

        code_list = []
        for line in content_lines:
            string=line.strip() #remove "'.
            
            
            self.diagnosis_matcher.add("DIAGNOSIS", None, self.nlp_priv(string))
            
            #bypass, jason
            #p = re.compile('([A-Z]+[0-9]+) (.+)')
            #m = p.match( string )

            if 0: #if m
                code = m.group(1)
                if (code not in code_list):
                    code_list.append(code)
                    diag_strings = m.group(2)
                    str2 = s.extract_diagnosis(diag_strings)
                    #print (str2)
                    
                    for item in str2:
                        item_10=item.strip() #remove "'.
                        item_1=item_10.strip('"')
                        if(code=="Z100"):
                            print(len(code), len(item_1))
                        self.diagnosis_matcher.add("DIAGNOSIS", None, self.nlp_priv(item_1))

                else:
                    #print("Code already processed, skip", code)
                    x=1
            else:
                #print("Code matching: missed special case", code)
                x=1

            #print(code_list)
            
            self.admission_date_matcher.add('ADMISSION_DATE', None,
                                  [{'LOWER': {'REGEX': 'admission'}}, {'LOWER': {'REGEX': 'date'}}, {"IS_PUNCT": True},
            {"TEXT": {'REGEX': '[0-1]?[0-9]/[0-3]?[0-9]/[1-2]?[0-9]?[0-9][0-9]'}}],
                                  [{'LOWER': {'REGEX': 'admission'}}, {'LOWER': {'REGEX': 'date'}}, {"IS_PUNCT": True}, {'ORTH': '['}, 
            {'ORTH': '*'}, {'ORTH': '*'}, {"IS_DIGIT": True}, {'ORTH': '-'}, {"IS_DIGIT": True}, {'ORTH': '-'}, {"IS_DIGIT": True}]
                                  )
            
            self.discharge_date_matcher.add('DISCHARGE_DATE', None,
                                  [{'LOWER': {'REGEX': 'discharge'}}, {'LOWER': {'REGEX': 'date'}}, {"IS_PUNCT": True},
            {"TEXT": {'REGEX': '[0-1]?[0-9]/[0-3]?[0-9]/[1-2]?[0-9]?[0-9][0-9]'}}],
                                  [{'LOWER': {'REGEX': 'discharge'}}, {'LOWER': {'REGEX': 'date'}}, {"IS_PUNCT": True}, {'ORTH': '['}, 
            {'ORTH': '*'}, {'ORTH': '*'}, {"IS_DIGIT": True}, {'ORTH': '-'}, {"IS_DIGIT": True}, {'ORTH': '-'}, {"IS_DIGIT": True}]
                                  )
            
            self.temperature_matcher.add('TEMPERATURE', None,
                                  [{'LOWER': {'REGEX': 'temperature'}}]
                                  )
            
            self.blood_pressure_matcher.add('BLOOD_PRESSURE', None,
                                  [{'LOWER': {'REGEX': 'blood'}}, {'LOWER': {'REGEX': 'pressure'}}]
                                  )
            
        
        
    def __call__(self, doc):
        logging.debug("Called UnitAnnotator Component")
        nlp = self.nlp
        
        
        with doc.retokenize() as retokenizer:
            
            # record_id 
            matches = self.record_id_matcher(doc)
            for match_id, start, end in matches:
                
                if (doc[end-1].ent_iob_!="") :
                    #end=end-1
                    print("Error with record_id", doc[end-1].ent_iob_, doc[end-1])
                    continue
                    
                #bypass the first two token
                my_start = start + 2
                my_end = end + 2
                
                if(doc[my_start].is_digit!=True and doc[my_start].like_num!=True):
                    print("Record ID Special Case", doc[my_start])
                    break
                
                span = Span(doc, my_start, my_end, label=nlp.vocab.strings['record_id'])
                for token in span:
                    token._.feature_is_record_id = True
                try:
                    if len(span) > 1:
                        retokenizer.merge(span)
                except ValueError:
                    pass
                doc.ents = list(doc.ents) + [span]
                
        with doc.retokenize() as retokenizer:
            #match and tag mass units
            matches = self.mass_matcher(doc)
            for match_id, start, end in matches:
                span = Span(doc, start, end, label=nlp.vocab.strings['mass_unit'])
                if span is None:
                    raise BaseException("Span is none")
                for token in span:
                    token._.feature_is_mass_unit = True
                try:
                    if len(span) > 1:
                        retokenizer.merge(span)
                except ValueError:
                    pass
                doc.ents = list(doc.ents) + [span]

        with doc.retokenize() as retokenizer:
            #match and tag volume units
            matches = self.volume_matcher(doc)
            for match_id, start, end in matches:
                span = Span(doc, start, end, label=nlp.vocab.strings['volume_unit'])
                for token in span:
                    token._.feature_is_volume_unit = True
                try:
                    if len(span) > 1:
                        retokenizer.merge(span)
                except ValueError:
                    pass
                doc.ents = list(doc.ents) + [span]


        with doc.retokenize() as retokenizer:
            # match and tag time units
            matches = self.time_matcher(doc)
            for match_id, start, end in matches:
                span = Span(doc, start, end, label=nlp.vocab.strings['time_unit'])
                for token in span:
                    token._.feature_is_time_unit = True
                if len(span) > 1:
                    retokenizer.merge(span)
                doc.ents = list(doc.ents) + [span]

        with doc.retokenize() as retokenizer:
            # durations
            matches = self.duration_matcher(doc)
            
            for match_id, start, end in matches:
                #print("DURATION:=====", start, end-1, doc[start], doc[end-1])
                
                for i in range(1,4):
                    if (doc[end-1].ent_iob_!=""):
                        end=end-1
                    elif (doc[start].ent_iob_!=""):
                        start=start+1
                    else:
                        break
                        
                    if (end<=start):
                        break
                    else:
                        continue
                        
                if (end<=start):
                    continue    
                
                span = Span(doc, start, end, label=nlp.vocab.strings['duration_pattern'])
                
                for token in span:
                    token._.feature_is_duration_pattern = True
                try:
                    if len(span) > 1:
                        retokenizer.merge(span)
                except ValueError:
                    pass

                try:
                    doc.ents = list(doc.ents) + [span]
                except:
                    print("duration_pattern exception", doc[start], doc[end-1])
                    continue


        with doc.retokenize() as retokenizer:

            # match and frequency indicators
            matches = self.frequency_matcher(doc)
            for match_id, start, end in matches:
                if (doc[end-1].ent_iob_!="") :
                    end=end-1
                    if (end == start):
                        break
                    
                span = Span(doc, start, end, label=nlp.vocab.strings['frequency_indicator'])
                
                for token in span:
                    token._.feature_is_frequency_indicator = True
                try:
                    if len(span) > 1:
                        retokenizer.merge(span)
                except ValueError:
                    pass
                doc.ents = list(doc.ents) + [span]

        with doc.retokenize() as retokenizer:
            #match and tag form units
            matches = self.form_matcher(doc)
            spans = []
            for match_id, start, end in matches:
                span = Span(doc, start, end, label=nlp.vocab.strings['form_unit'])
                for token in span:
                    token._.feature_is_form_unit = True
                try:
                    if len(span) > 1:
                        retokenizer.merge(span)
                except ValueError:
                    pass
                doc.ents = list(doc.ents) + [span]

        with doc.retokenize() as retokenizer:
            # match and tag route types
            matches = self.route_matcher(doc)
            for match_id, start, end in matches:
                
                for i in range(1,4):
                    if (doc[end-1].ent_iob_!=""):
                        end=end-1
                    elif (doc[start].ent_iob_!=""):
                        start=start+1
                    else:
                        break
                        
                    if (end<=start):
                        break
                    else:
                        continue
                        
                if (end<=start):
                    continue
                    
                span = Span(doc, start, end, label=nlp.vocab.strings['route_type'])
                
                #if (start==391):
                    #print("JAson===========391 BEFOR", start, end, doc[start], doc[end-1], len(doc))
                    
                for token in span:
                    token._.feature_is_route_type = True
                    try:
                        if len(span) > 1:
                            retokenizer.merge(span)
                    except ValueError:
                        pass
                    #doc.ents = list(doc.ents) + [span]
                    if (start==391):
                        #start1=doc.ents[-1].start
                        #end1=doc.ents[-1].end
                        start1=start
                        end1=end
                        #print("JAson====XXXXX====391 AFTER", start1, end1, doc[start1], doc[end1-1], len(doc))
                    
                doc.ents = list(doc.ents) + [span]
                        
                        
        with doc.retokenize() as retokenizer:
            # match units of measurement (x/y, , etc)
            matches = self.unit_of_measurement_matcher(doc)
            for match_id, start, end in matches:
                span = Span(doc, start, end, label=nlp.vocab.strings['measurement_unit'])
                for token in span:
                    token._.feature_is_measurement_unit = True
                try:
                    if len(span) > 1:
                        retokenizer.merge(span)
                except ValueError:
                    pass
                
                try:
                    doc.ents = list(doc.ents) + [span]
                except ValueError:
                    print("exception at measurement_unit", doc[start], doc[end-1])
                    continue

        with doc.retokenize() as retokenizer:

            # units of measures, numbers , percentages all together
            matches = self.measurement_matcher(doc)
            for match_id, start, end in matches:
                if (doc[end-1].ent_iob_!="") :
                    end=end-1
                    
                span = Span(doc, start, end, label=nlp.vocab.strings['measurement'])
                for token in span:
                    token._.feature_is_measurement = True
                try:
                    if len(span) > 1:
                        retokenizer.merge(span)
                except ValueError:
                    pass
                doc.ents = list(doc.ents) + [span]


        with doc.retokenize() as retokenizer:

            # Clock 
            matches = self.clock_matcher(doc)
            for match_id, start, end in matches:
                if (doc[end-1].ent_iob_!="") :
                    end=end-1
                    
                span = Span(doc, start, end, label=nlp.vocab.strings['clock'])
                for token in span:
                    token._.feature_is_clock = True
                try:
                    if len(span) > 1:
                        retokenizer.merge(span)
                except ValueError:
                    pass
                doc.ents = list(doc.ents) + [span]

        with doc.retokenize() as retokenizer:

            # drug 
            matches = self.drug_matcher(doc)
            for match_id, start, end in matches:
                #print("DRUG:=====", start, end-1, doc[start], doc[end-1])
                
                for i in range(1,4):
                    if (doc[end-1].ent_iob_!=""):
                        end=end-1
                    elif (doc[start].ent_iob_!=""):
                        start=start+1
                    else:
                        break
                        
                    if (end<=start):
                        break
                    else:
                        continue
                     
                        
                if (end<=start):
                    continue
                
                span = Span(doc, start, end, label=nlp.vocab.strings['drug'])
                for token in span:
                    token._.feature_is_drug = True
                try:
                    if len(span) > 1:
                        retokenizer.merge(span)
                except ValueError:
                    pass
                doc.ents = list(doc.ents) + [span]
                

        with doc.retokenize() as retokenizer:

            # diagnosis 
            matches = self.diagnosis_matcher(doc)
            for match_id, start, end in matches:
                if (doc[end-1].ent_iob_!="") :
                    end=end-1
                    
                span = Span(doc, start, end, label=nlp.vocab.strings['diagnosis'])
                for token in span:
                    token._.feature_is_diagnosis = True
                try:
                    if len(span) > 1:
                        retokenizer.merge(span)
                except ValueError:
                    pass
                doc.ents = list(doc.ents) + [span]
                
        with doc.retokenize() as retokenizer:

            # admission_date 
            matches = self.admission_date_matcher(doc)
            for match_id, start, end in matches:
                if (doc[end-1].ent_iob_!="") :
                    #end=end-1
                    print("Error with admission_date", doc[end-1].ent_iob_, doc[end-1])
                    continue
                    
                #only take the last token for like 11/02/2002
                if (end-start == 4):
                    my_start=end-1
                    #print(doc[end-1])
                elif (end-start == 11):
                    my_start=end-5 # take the last five tokens for like 2002-11-02
                else:
                    print("Error with admission_date", doc[end-1].ent_iob_, doc[end-1]) #unexpected match
                    
                span = Span(doc, my_start, end, label=nlp.vocab.strings['admission_date'])
                for token in span:
                    token._.feature_is_admission_date = True
                try:
                    if len(span) > 1:
                        retokenizer.merge(span)
                except ValueError:
                    pass
                doc.ents = list(doc.ents) + [span]
                
        with doc.retokenize() as retokenizer:

            # discharge_date 
            matches = self.discharge_date_matcher(doc)
            for match_id, start, end in matches:
                if (doc[end-1].ent_iob_!="") :
                    #end=end-1
                    print("Error with discharge_date", doc[end-1].ent_iob_, doc[end-1])
                    continue
                    
                #only take the last token for like 11/02/2002
                if (end-start == 4):
                    my_start=end-1
                    #print(doc[end-1])
                elif (end-start == 11):
                    my_start=end-5 # take the last five tokens for like 2002-11-02
                else:
                    print("Error with discharge_date", doc[end-1].ent_iob_, doc[end-1]) #unexpected match
                    
                span = Span(doc, my_start, end, label=nlp.vocab.strings['discharge_date'])
                for token in span:
                    token._.feature_is_discharge_date = True
                try:
                    if len(span) > 1:
                        retokenizer.merge(span)
                except ValueError:
                    pass
                doc.ents = list(doc.ents) + [span]
                
        with doc.retokenize() as retokenizer:

            # temperature 
            matches = self.temperature_matcher(doc)
            for match_id, start, end in matches:
                if (doc[end-1].ent_iob_!="") :
                    #end=end-1
                    print("Error with temperature", doc[end-1].ent_iob_, doc[end-1])
                    continue
                    
                #search for temperature token
                found = False
                
                for x in range(0, 10):
                    my_pos=end + x
                    #print(doc[my_pos])
                    if (doc[my_pos].is_punct == True):
                        break
                    elif (doc[my_pos].like_num == True):
                        found = True
                        break
                    else:
                        continue
                    
                if (found == False):
                    break
                else:
                    my_start = my_pos
                    my_end = my_pos + 1
                    
                
                span = Span(doc, my_start, my_end, label=nlp.vocab.strings['temperature'])
                for token in span:
                    token._.feature_is_temperature = True
                try:
                    if len(span) > 1:
                        retokenizer.merge(span)
                except ValueError:
                    pass
                
                try:
                    doc.ents = list(doc.ents) + [span]
                except:
                    print("temperature exception", doc[my_start], doc[my_end-1])
                    continue
                
        with doc.retokenize() as retokenizer:
            
            # blood_pressure 
            matches = self.blood_pressure_matcher(doc)
            for match_id, start, end in matches:
                if (doc[end-1].ent_iob_!="") :
                    #end=end-1
                    print("Error with blood_pressure", doc[end-1].ent_iob_, doc[end-1])
                    continue
                    
                #search for temperature token
                found = False
                p = re.compile('[1-2]?[0-9][0-9]/[0-1]?[0-9][0-9]')
                
                for x in range(0, 10):
                    my_pos=end + x
                              
                    if (doc[my_pos].is_punct == True):
                        break
                    elif (p.match( doc[my_pos].text ) != None):
                        found = True
                        break
                    else:
                        continue
                    
                if (found == False):
                    break
                else:
                    my_start = my_pos
                    my_end = my_pos + 1
                    
                
                span = Span(doc, my_start, my_end, label=nlp.vocab.strings['blood_pressure'])
                for token in span:
                    token._.feature_is_blood_pressure = True
                try:
                    if len(span) > 1:
                        retokenizer.merge(span)
                except ValueError:
                    pass
                try:
                    doc.ents = list(doc.ents) + [span]
                except:
                    print("blood_pressure exception", doc[my_start], doc[my_end-1])
                    continue
                
                
        return doc
    

    
    
class Extract_Med_Features:

    def extract_diagnosis(self, string):
    
        match_items =[]
        if (re.search("\[", string) != None ): # matching with '['
            #str1="Disseminated intravascular coagulation [defibrination syndrome]"
            #str2="Unspecified mood [affective] disorder"

            p = re.compile('(.+) \[(.+)\](.+)?')
            m = p.match( string )

            if m:
                if (m.group(3)!= None):
                    matches = {m.group(1)+m.group(3), m.group(2)+m.group(3)}
                else:
                    matches = {m.group(1), m.group(2)}

                match_items.extend(matches)

            else:
                print("with '[': missed special case")

        elif (re.search("\(", string) != None ): # matching with '('

            new_string = {string}

            #print("New string-----",new_string)

            for item in new_string:
                if (re.search("\(s\)", item) != None  ): # special case with "(s)"

                    #str9="Fracture of rib(s), sternum and thoracic spine"
                    match_items.extend({item})

                elif (re.search("and", item) != None ): # with 'and' in description

                    #str6="Subsequent ST elevation (STEMI) and non-ST elevation (NSTEMI) myocardial infarction"
                    p = re.compile('(.+) \((..+)\) and (.+) \((..+)\)(.+)')
                    m = p.match( item )

                    if m:
                        matches = {m.group(1)+m.group(5), m.group(2)+m.group(5), m.group(3)+m.group(5), m.group(4)+m.group(5)}
                        match_items.extend(matches)
                    else:
                        #print("with 'and' in description: missed special case", item)
                        x=1

                elif (len(re.findall("\(", item)) >1 ): #double "("

                    #str8="Contact with birds (domestic) (wild)"
                    p = re.compile('(.+) \((.+)\) \((.+)\)')
                    m = p.match(item)

                    if m:
                        matches = {m.group(1)}
                        match_items.extend(matches)                
                    else:
                        print("double brackets: 'missed special case'")

                else: #single
                    if (re.search("by", item) != None ): # with 'by' in description
                        p = re.compile('(.+) by (.+) \((..+)\)(.+)?')
                        m = p.match( item )

                        if m:
                            if (m.group(4)!= None):
                                matches = {m.group(1)+' by '+m.group(2)+m.group(4), m.group(1)+' by '+m.group(3)+m.group(4)}
                            else:
                                matches = {m.group(1)+' by '+m.group(2), m.group(1)+' by '+m.group(3)}

                            match_items.extend(matches)
                        else:
                            print("single '(' by: missed special case")

                    else:

                        #str4="Chlamydial lymphogranuloma (venereum)"
                        #str5="Newborn affected by intrauterine (fetal) blood loss"
                        #str7="Chronic kidney disease (CKD)"
                        p = re.compile('(.+) \((..+)\)(.+)?')
                        m = p.match( item )

                        if m:
                            if (m.group(3)!= None):
                                matches = {m.group(1)+m.group(3), m.group(2)+m.group(3)}
                            else:
                                matches = {m.group(1), m.group(2)}

                            match_items.extend(matches)        
                        else:
                            print("single '(' non-by: missed special case")

        else:
            #str3="C50 Malignant neoplasm of upper-inner quadrant of breast, female"
            match_items = {string}

        return(match_items)
