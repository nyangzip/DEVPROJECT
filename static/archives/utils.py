# -*- coding: utf-8 -*-
"""
Created on Tue Nov 16 17:44:53 2021

@author: Nghia
"""

def str_date_to_int(str_date: str) -> int: #format "m(m)/d(d)/yyyy"
    m,d,y = list(map(int,str_date.split('/')))
    int_date = (y*100 + m)*100+d
    return int_date

def find_patient_within_date(patients: dict, str_date_1: str, str_date_2: str) -> dict:
    int_date_1 = str_date_to_int(str_date_1)
    int_date_2 = str_date_to_int(str_date_2)
    
    min_date = min(int_date_1, int_date_2)
    max_date = max(int_date_1, int_date_2)
    
    filtered_patient_list = {}
    
    for pid in patients:
        if (patients[pid]['date'] >= min_date) and (patients[pid]['date'] <= max_date):
            filtered_patient_list[pid] = patients[pid]
            
    return filtered_patient_list

def tree_spread(patients: dict) -> dict:
    tree_patients = {}
    tree_id = 0
    
    low = []
    for pid in patients.keys():
        low += patients[pid]['branch']
    low = [l for l in low if l in patients]
    
    low = set(low)
    high = set(patients.keys()) - low
    
    while low and high:
        tree_patients[tree_id] = {}
        for hid in high:
            tree_patients[tree_id][hid] = patients[hid]
    
        tree_id += 1
        tree_patients[tree_id] = {}
        for lid in low:
            tree_patients[tree_id][lid] = patients[lid]
        
        new_patients = tree_patients[tree_id]
        
        low = []
        for pid in new_patients.keys():
            low += new_patients[pid]['branch']
        low = [l for l in low if l in patients]
        
        low = set(low)
        high = set(new_patients.keys()) - low
    
    return tree_patients