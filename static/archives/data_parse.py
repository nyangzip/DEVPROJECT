# -*- coding: utf-8 -*-
"""
Created on Thu Oct 28 15:04:45 2021

@author: Nghia
"""

import numpy as np
import pandas as pd
import utils
import json

df = pd.read_csv('PatientInfo.csv')

province_list = set(df.province)
city_list = set(df.city)
patient_list = set(df.patient_id)

patients = {}

for _, row in df.iterrows():
    pid = str(row.patient_id)
    
    if pid not in patients:
        patients[pid] = {'province':row.province, 'city':row.city, 'date':utils.str_date_to_int(row.confirmed_date), 'branch':[]}
    else:
        #if already created before, update it
        patients[pid]['province']=row.province
        patients[pid]['city']=row.city
        patients[pid]['date']=utils.str_date_to_int(row.confirmed_date)
        
    if pd.notna(row.infected_by):
        iid = str(int(row.infected_by))
        if iid == pid:
            #sometimes, patient is infected by himself. wtf is this logic?
            continue
        if iid not in patients:
            #if havent seen before, create it
            patients[iid] = {'province':None, 'city':None, 'date':None, 'branch':[]}
            
        patients[iid]['branch'].append(pid)

province_codes = pd.read_csv('static/province_code.csv')
city_codes = pd.read_csv('static/city_code.csv')

new_patients = {}

for pid in patients:
    new_patients[pid] = {}
    new_patients[pid]['date'] = patients[pid]['date']
    new_patients[pid]['branch'] = patients[pid]['branch']
    
    province = patients[pid]['province']
    city = patients[pid]['city']
    pc = province_codes.loc[province_codes.province == province].province_code.iloc[0]
    if city == 'etc':
        cc = city_codes.loc[(city_codes.province_code == pc)].city_code.iloc[0]
    else:
        cc = city_codes.loc[(city_codes.province_code == pc) & (city_codes.city == city)].city_code.iloc[0]
    
    new_patients[pid]['code'] = str(pc*1000+cc)
    
# with open('static/transmission.json', 'w') as f:
#     json.dump(new_patients, f)

date_1 = '02/24/2019'
date_2 = '02/20/2021'
flist = utils.find_patient_within_date(new_patients, date_1, date_2)
tree_patients = utils.tree_spread(flist)