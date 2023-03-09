### THE FOLLLOWING TWO FUNCTIONS ARE FROM CDL_HELPER.PY IN THE ANALYSIS FOLDER
### THEY SHOULD BE PLACED INTO A COMMON FILE THAT CAN BE ACCESSED IN BOTH DIRECTORIES IN THE FUTURE

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from reformatter import reshape_match
from sklearn.ensemble import RandomForestClassifier

def read_in_list(ids):
    frames = []
    for idd in ids:
        frames.append(pd.read_csv(f'../data/cdl_{idd}.csv'))
    return pd.concat(frames)

def read_in_all_matches() -> pd.DataFrame:
    matchIDs = pd.read_json('../major_ids.json')

    m1_qual = read_in_list(matchIDs['major1'][0])
    m2_qual = read_in_list(matchIDs['major2'][0])
    m2_event = read_in_list(matchIDs['major2'][1])
    m3_qual = read_in_list(matchIDs['major3'][0])

    m1_qual['event'] = ['M1Qual' for i in m1_qual[m1_qual.columns[0]]]
    m2_qual['event'] = ['M2Qual' for i in m2_qual[m2_qual.columns[0]]]
    m3_qual['event'] = ['M3Qual' for i in m3_qual[m3_qual.columns[0]]]
    m2_event['event'] = ['M2Event' for i in m2_event[m2_event.columns[0]]]

    m1_qual['setting'] = ['online' for i in m1_qual[m1_qual.columns[0]]]
    m2_qual['setting'] = ['online' for i in m2_qual[m2_qual.columns[0]]]
    m3_qual['setting'] = ['online' for i in m3_qual[m3_qual.columns[0]]]
    m2_event['setting'] = ['lan' for i in m2_event[m2_event.columns[0]]]

    complete_df = pd.concat([m1_qual, m2_event, m2_qual, m3_qual])

    return complete_df

############################################################################################################

from sklearn.preprocessing import LabelEncoder

label_encoder = LabelEncoder()

def reshape_all():
    df = read_in_all_matches()
    df = reshape_match(df)
    return df

def hardpoint_model(predict_data):
    dat = reshape_all()
    hard = dat[dat['mode']=='CDL Hardpoint'].drop(['fbPerc_team1', 'fbPerc_team2'], axis=1)
    hard.dropna(how='any', axis=0, inplace=True)
    hard['winner'] = label_encoder.fit_transform(hard['winner'])
    trainX = hard.drop(['winner', 'mode'], axis=1)
    trainY = hard['winner']
    rf = RandomForestClassifier(max_depth=11, n_estimators=67)
    rf.fit(trainX, trainY)
    prediction = rf.predict(predict_data)
    return prediction

def control_model(predict_data):
    dat = reshape_all()
    cnt = dat[dat['mode']=='CDL Control'].drop(['fbPerc_team1', 'fbPerc_team2', 'rotationalPercent_team1', 'rotationalPercent_team2'], axis=1)
    cnt.dropna(how='any', axis=0, inplace=True)
    cnt['winner'] = label_encoder.fit_transform(cnt['winner'])
    trainX = cnt.drop(['winner', 'mode'], axis=1)
    trainY = cnt['winner']
    rf = RandomForestClassifier(max_depth=4, n_estimators=306)
    rf.fit(trainX, trainY)
    prediction = rf.predict(predict_data)
    return prediction

def snd_model(predict_data):
    dat = reshape_all()
    snd = dat[dat['mode']=='CDL SnD'].drop(['rotationalPercent_team1', 'rotationalPercent_team2'], axis=1)
    snd.dropna(how='any', axis=0, inplace=True)
    snd['winner'] = label_encoder.fit_transform(snd['winner'])
    trainX = snd.drop(['winner', 'mode'], axis=1)
    trainY = snd['winner']
    rf = RandomForestClassifier(max_depth=17, n_estimators=71)
    rf.fit(trainX, trainY)
    prediction = rf.predict(predict_data)
    return prediction

