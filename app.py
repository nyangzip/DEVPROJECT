from flask import Flask, render_template, request, redirect, Response
# import csv
import datetime
from flask.helpers import url_for
import numpy as np
import os
import json
# export FLASK_ENV=development
# set FLASK_APP = app.py
# flask run -p 5500 (kakaomap api를 실행시키기 위해서 등록한 port를 이용해야하기 때문)

import requests,xmltodict

# import urllib.parse
import pandas as pd

app = Flask(__name__)

import update_COVID_DB ######## 이거를 추가
import os


##### 오전 11시를 지나지 않았으면 전날 꺼 받아오기
today_now = datetime.datetime.now()
if datetime.datetime.now().hour < 11:
    today_now = datetime.datetime.now() - datetime.timedelta(days=1)
else: 
    pass
yyyy = today_now.year; mm = today_now.month; dd = today_now.day
yyyy_str = str(yyyy); mm_str = str(mm).zfill(2); dd_str = str(dd).zfill(2)

##### 오전 11시 지났는데 파일이 만들어져있지 않으면 새로 업데이트하기
if os.path.isfile(f'static/archives/{yyyy_str}{mm_str}{dd_str}.json') == True: pass
else: update_COVID_DB.make_30_days_records(yyyy,mm,dd)

@app.route('/')
def main():
  return render_template('main.html')

@app.route('/index')
def index():
  return render_template('index.html')


@app.route('/current_status', methods=['GET','POST'])
def address():
  if request.method == 'POST':
    data = request.form['addname']
    print(data)
    print(data.split())
    regions = ['서울', '인천', '대전', '광주', '대구', '울산', '부산']
    if data.split()[0] in regions:
      # pddata = pd.read_csv('https://raw.githubusercontent.com/nyangzip/DEVPROJECT/master/TbCorona19CountStatusJCG_'+str(datetime.date.today().strftime('%Y-%m-%-d'))+'.csv',index=True,index_col='date')
      pddata = json.load(open('./static/archives/'+yyyy_str+mm_str+dd_str+'.json'))
      paramcsv = pd.DataFrame({'date':pddata['date'],'confirmed':pddata[' '.join(data.split()[:2])]['confirmedNumber']}).sort_values(by='date')
      paramcsv['confirmedsum'] = paramcsv['confirmed'].cumsum().astype(float)
      # paramcsv.pop('confirmed')
      # paramcsv.rename(columns={'confirmedsum':'confirmed'},inplace=True)
      paramcsv.to_csv('paramdata.csv',index=False) # Date , Confirmed
      # value = sum(pddata[' '.join(data.split()[:2])]['confirmedNumber'])
      maxvalue = max(pddata[' '.join(data.split()[:2])]['confirmedNumber'])
      SUMvalue = sum(pddata[data.split()[0]]['confirmedNumber']) # by city
      sumvalue = sum(pddata[' '.join(data.split()[:2])]['confirmedNumber']) # by Gu
      death = sum(pddata[' '.join(data.split()[:2])]['deathNumber'])
      try:
        rank1 = pddata[' '.join(data.split()[:2])]['origin'][0]
      except:
        rank1 = ' '
      try:        
        rank2 = pddata[' '.join(data.split()[:2])]['origin'][1]
      except:
        rank2 = ' '
      try:
        rank3 = pddata[' '.join(data.split()[:2])]['origin'][2]
      except:
        rank3 = ' '
      return render_template('current_status.html',data=' '.join(data.split()[:2]),value=int(sumvalue),death=int(death),city=data.split()[0],rank1=rank1,rank2=rank2,rank3=rank3,alldata = data, maxvalue= maxvalue, SUMvalue = SUMvalue)
    else :
      pddata = json.load(open('./static/archives/'+datetime.datetime.today().strftime('%Y%m%d')+'.json'))
      paramcsv = pd.DataFrame({'date':pddata['date'],'confirmed':pddata[data.split()[0]]['confirmedNumber']}).sort_values(by='date')
      paramcsv['confirmedsum'] = paramcsv['confirmed'].cumsum().astype(float)
      # paramcsv.pop('confirmed')
      # paramcsv.rename(columns={'confirmedsum':'confirmed'},inplace=True)
      paramcsv.to_csv('paramdata.csv',index=False) # Date , Confirmed
      # value = sum(pddata[' '.join(data.split()[:2])]['confirmedNumber'])
      maxvalue = max(pddata[data.split()[0]]['confirmedNumber'])
      SUMvalue = sum(pddata[data.split()[0]]['confirmedNumber']) # by city
      death = sum(pddata[data.split()[0]]['deathNumber'])
      return render_template('current_status_not.html',data=' '.join(data.split()[:2]),value=int(SUMvalue),death=int(death),city=data.split()[0],maxvalue= maxvalue,alldata = data)      
  elif request.method == 'GET':
    data = {}
    print(data)
    # raise SystemError
    return render_template('index.html')
  

# @app.route('/c')
# def transmission():
#   return render_template('transmission.html')

@app.route('/transmission')
def transmission():
  return render_template('transmission.html')

@app.route('/WhyVaccine')
def WhyVaccine():
  return render_template('WhyVaccine.html')


# @app.route('/<usr>')
# def user(usr):
#   return f'<h1>{usr}</h1>'

@app.route('/CVpdf')
def CVpdf():
  return render_template('CVpdf.html')

@app.route('/param.csv')
def output_dataframe_csv():
  with open('paramdata.csv','r') as p:
    open_read = p.readlines()
  page =''
  for ii in open_read:
    page += ii
  # a= pd.read_csv('paramdata.csv')
  return page

if __name__ == '__main__':
  app.run(debug=True)
