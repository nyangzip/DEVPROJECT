from flask import Flask, render_template, request, redirect
# import csv
import datetime
from flask.helpers import url_for
import numpy as np
import os
# export FLASK_ENV=development
# set FLASK_APP = app.py
# flask run -p 5500 (kakaomap api를 실행시키기 위해서 등록한 port를 이용해야하기 때문)

import requests,xmltodict
# import urllib.parse
import pandas as pd

app = Flask(__name__)

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
    # Check datafile
    try:
      pddata = pd.read_csv('https://raw.githubusercontent.com/nyangzip/DEVPROJECT/master/TbCorona19CountStatusJCG_'+str(datetime.date.today())+'.csv',index=True,index_col='date')
    except:
      # Connecting data district with local index need
      confirmed = []
      date_data = []
      for ii in range(30):
          date='.'.join(str(datetime.date.today() - datetime.timedelta(days=ii+1)).split('-'))+'.00'
          date_index = '.'.join(str(datetime.date.today() - datetime.timedelta(days=ii+1)).split('-'))
          serviceurl = 'http://openAPI.seoul.go.kr:8088/5343646e4762616b3637774c504971/xml/TbCorona19CountStatusJCG/1/100/' + date
          resp = requests.get(serviceurl)
          coronadist = xmltodict.parse(resp.content)
          try:
              a=coronadist['TbCorona19CountStatusJCG']['row']
              confirmed.append(int(a['SDMADD']))
              date_data.append(date_index)
          except:
              confirmed.append(np.nan)
              date_data.append(date_index)
      pddata=pd.DataFrame({'confirmed':confirmed},index=date_data).sort_index(ascending=True)
      pddata.confirmed = pddata.confirmed.fillna(0).cumsum()
      pddata.to_csv('TbCorona19CountStatusJCG_'+str(datetime.date.today())+'.csv',index=True,index_label='date')
      # os.system('git remote add origin https://github.com/nyangzip/DEVPROJECT.git')
      # os.system('git push -u origin main')
      # os.system('git config --global user.email "bakerson111@gmail.com"')
      # os.system('git config --global user.name "JongminKim"')
      # os.system('git pull')
      # os.system('git commit -m "data update"')
    try:
      deathdata = pd.read_csv('deathdata'+''.join(str(datetime.date.today()).split('-'))+'.csv')
    except:
      serviceurl = 'http://openapi.data.go.kr/openapi/service/rest/Covid19/getCovid19SidoInfStateJson?serviceKey=2t52ye5eVy%2FenbN2RzxWVtkLSp1k44J3m4PQslsjH1TA3WIEs1vyOlwcLv5TrlVL15QxJlfjwzNp77l8114wOA%3D%3D'
      params ={'pageNo' : '1',
      'numOfRows' : '10',
      'startCreateDt' : ''.join(str(datetime.date.today() - datetime.timedelta(days=30)).split('-')),
      'endCreateDt' : ''.join(str(datetime.date.today()).split('-')) }
      resp = requests.get(serviceurl,params=params)
      dictdata = xmltodict.parse(resp.content)
      deathdata=pd.DataFrame(dictdata['response']['body']['items']['item'])
      deathdata.to_csv('deathdata'+''.join(str(datetime.date.today()).split('-'))+'.csv')
      # os.system('git remote add origin https://github.com/nyangzip/DEVPROJECT.git')
      # os.system('git push -u origin main')
      # os.system('git config --global user.email "bakerson111@gmail.com"')
      # os.system('git config --global user.name "JongminKim"')
      # os.system('git pull')
      # os.system('git commit -m "data update"')
    value = pddata.confirmed[-1]
    death = list(deathdata[deathdata['gubun']==data.split()[0]]['deathCnt'])[0]
    return render_template('current_status.html',data=' '.join(data.split()[:2]),value=value,death=death,city=data.split()[0])

  elif request.method == 'GET':
    data = {}
    print(data)
    raise SystemError
    return render_template('index.html')
  
  


@app.route('/<usr>')
def user(usr):
  return f'<h1>{usr}</h1>'

if __name__ == '__main__':
  app.run(debug=True)
