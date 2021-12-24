import numpy as np
import pandas as pd
import datetime as dt
from collections import Counter

import glob
import os

import json

import ssl
import urllib.request
import requests
from bs4 import BeautifulSoup


#### update files in last 2 month folder
def bring_2months(str_cityNm_eng, df_updated_result):
    
    new_result = df_updated_result
    
    result_2m_path = f'./static/archives/last_2_months/CORONA_{str_cityNm_eng}.csv'    
    pre_result = pd.read_csv(result_2m_path, encoding='euc-kr')
    Result = pd.concat([new_result, pre_result], ignore_index=True).drop_duplicates().sort_values(by='c_date', ascending=False)
    
    if len(Result.c_date.str.slice(stop=7).unique()) > 2:
        
        this_months = np.sort(Result.c_date.str.slice(stop=7).unique())[-2:]
        this_Result = Result[Result.c_date.str.startswith(this_months[0])|Result.c_date.str.startswith(this_months[1])]
        
        past_Result = Result[~(Result.c_date.str.startswith(this_months[0])|Result.c_date.str.startswith(this_months[1]))]
        
        past_result_path = f'./static/archives/past/CORONA_{str_cityNm_eng}.csv'
        past_result = pd.read_csv(past_result_path, encoding='euc-kr')
        past_Result = pd.concat([past_Result, past_result]).drop_duplicates().sort_values(by='p_idx', ascending=False)
        past_Result.to_csv(past_result_path, encoding='euc-kr', index=False)
                
    else:
        this_Result = Result
        
    this_Result.to_csv(result_2m_path, encoding='euc-kr', index=False)
    
    return this_Result


#### for Seoul
def dataUpdate_seoul():

    url_seoul = 'https://news.seoul.go.kr/api/27/getCorona19Status/get_status_ajax.php?length=5000'
    req_seoul = urllib.request.Request(url_seoul)
    response_seoul = urllib.request.urlopen(req_seoul).read().decode('euc-kr')
    
    retData = json.loads(response_seoul)
    
    p_idx = [aa[0].split('>')[1].split('<')[0] for aa in retData['data']]
    c_date = [aa[2] for aa in retData['data']]
    SGG = [aa[3] for aa in retData['data']]
    origin = [aa[5] for aa in retData['data']]

    new_result = pd.DataFrame({'p_idx':p_idx, 'c_date':c_date, 'SGG':SGG, 'origin':origin})
    new_result.SGG = new_result.SGG.str.replace(' ','', regex=True)
    new_result.SGG = '서울 '+new_result.SGG
    new_result.p_idx = new_result.p_idx.astype(int)

    return bring_2months('seoul', new_result)


#### for Busan
def dataUpdate_busan():

    url_busan = 'https://www.busan.go.kr/covid19/JsonCourse.do?lastIndex=2000'
    req_busan = urllib.request.Request(url_busan)
    response_busan = urllib.request.urlopen(req_busan).read().decode('euc-kr')
    
    retData_busan = json.loads(response_busan)
    
    p_idx = [aa['idx'] for aa in retData_busan[0]]
    c_date = [aa['confirmdate'] for aa in retData_busan[0]]
    SGG = [aa['area'] for aa in retData_busan[0]]
    
    new_result = pd.DataFrame({'p_idx':p_idx,'c_date':c_date, 'SGG':SGG})
    new_result.SGG = '부산 '+new_result.SGG
    new_result.c_date = ['2021-'+bb.split('.')[0].zfill(2)+'-'+bb.split('.')[1][1:].zfill(2) for bb in new_result.c_date]
    new_result.p_idx = new_result.p_idx.astype(int)

    return bring_2months('busan', new_result)


#### for Daegu
def dataUpdate_daegu():

    root_url_daegu = r'https://www.daegu.go.kr/icms/bbs/selectBoardList.do?bbsId=BBS_02098&postPerPage=5&pageIndex=1'
    root_req_daegu = requests.get(root_url_daegu)
    root_soup_daegu = BeautifulSoup(root_req_daegu.content, 'html.parser')
    
    seg_num_list = [aa['onclick'].split(' ')[1].split(')')[0][1:-1] for aa in root_soup_daegu.find_all('a') if ('대응 관련 브리핑' in aa.text)]
    
    for s_idx, seg_num in enumerate(seg_num_list):
        
        url_daegu = f'https://www.daegu.go.kr/icms/bbs/selectBoardArticle.do?bbsId=BBS_02098&nttId={seg_num}'
        req_daegu = requests.get(url_daegu)
        soup_daegu = BeautifulSoup(req_daegu.content, 'html.parser')

        date = soup_daegu.select('dd')[0].text.split('] ')[1].split(' ')[0].split('.(')[0]
        Date = date.split('.')[0]+'-'+date.split('.')[1].zfill(2)+'-'+date.split('.')[2].zfill(2)
    
        p_idx = [aa.text for aa in soup_daegu.select('table')[-1].select( 'tbody > tr > td')[1::4]][1:]
        c_date = [Date] * len(p_idx)
        SGG = [aa.text for aa in soup_daegu.select('table')[-1].select( 'tbody > tr > td')[2::4]][1:]
        t_path = [aa.text for aa in soup_daegu.select('table')[-1].select( 'tbody > tr > td')[3::4]][1:]

        new_result = pd.DataFrame({'p_idx':p_idx, 'c_date':c_date, 'SGG':SGG, 'origin':t_path})
        new_result.SGG = '대구 '+new_result.SGG
        
        new_result.p_idx = new_result.p_idx.str.replace('\n', '', regex=True).str.replace('#', '', regex=True).str.replace('*', '', regex=True)
        new_result.p_idx = new_result.p_idx.astype(int)
        
        new_result.SGG = new_result.SGG.str.replace('\n','', regex=True)
        new_result.origin = new_result.origin.str.replace('\n· |\n|⸳ |⸱ |‧ |・','', regex=True)
        new_result.origin = new_result.origin.str.replace('\xa0','/', regex=True)
        
        if s_idx == 0:
            New_result = new_result
        else:
            New_result = pd.concat([New_result, new_result])
            
    New_result = New_result.sort_values(by='p_idx', ascending=False)
    
    return bring_2months('daegu', New_result)


#### for Incheon
def dataUpdate_incheon():
    
    for pageNum in np.arange(1,50):
        
        url_incheon = f'https://www.incheon.go.kr/fnct/corona/mainSumTab1.json?curPage={pageNum}&cntPerPage=100'
        
        ctx = ssl.create_default_context()
        ctx.check_hostname = False
        ctx.verify_mode = ssl.CERT_NONE

        req_incheon = urllib.request.Request(url_incheon)
        response_incheon = urllib.request.urlopen(req_incheon, context=ctx).read()

        retData_incheon = json.loads(response_incheon)

        p_idx = [aa['mainNo'] for aa in retData_incheon['list']['listObject']]
        c_date = [aa['firstDate'] for aa in retData_incheon['list']['listObject']]
        SGG = [aa['patientArea'] for aa in retData_incheon['list']['listObject']]

        new_result = pd.DataFrame({'p_idx':p_idx, 'c_date':c_date, 'SGG':SGG})

        if pageNum == 1:
            New_result = new_result
        else:
            New_result = pd.concat([New_result, new_result], ignore_index=True)
            
    New_result.c_date = ['20'+bb.split('/')[2]+'-'+bb.split('/')[0].zfill(2)+'-'+bb.split('/')[1].zfill(2) for bb in New_result.c_date.values]
    New_result.p_idx = New_result.p_idx.astype(int)
    New_result.SGG = '인천 '+New_result.SGG
    
    return bring_2months('incheon', New_result)

#### for Gwangju
def dataUpdate_gwangju():
    
    url_gwangju = 'https://www.gwangju.go.kr/c19/covid19ConfiremListHome.do'
    req_gwangju = urllib.request.Request(url_gwangju)
    response_gwangju = urllib.request.urlopen(req_gwangju).read()

    retData_gwangju = json.loads(response_gwangju)
    
    num_for_day = 200
    
    p_idx = [int(aa['CONF_NUMBER'].replace('광주 ','')) for aa in retData_gwangju['list'][:num_for_day]]
    c_date = ['2021-'+aa['CONF_DATE'].split(' ')[0].replace('월','').zfill(2)+'-'+aa['CONF_DATE'].split(' ')[1].replace('일','').zfill(2) for aa in retData_gwangju['list'][:num_for_day]]
    SGG = [aa['PERSONAL_DATA'] for aa in retData_gwangju['list'][:num_for_day]]
    t_path = [aa['INFECTION_PROCESS'] for aa in retData_gwangju['list'][:num_for_day]]

    new_result = pd.DataFrame({'p_idx':p_idx,'c_date':c_date, 'SGG':SGG, 'origin':t_path})
    new_result =new_result.sort_values(by='p_idx', ascending=False)
    new_result.origin = new_result.origin.str.replace('‧','·', regex=True)

    return bring_2months('gwangju', new_result)


#### for Daejeon
def dataUpdate_daejeon():
    
    url_daejeon = f'https://www.daejeon.go.kr/corona19/index.do?menuId=0002'
    req_daejeon = requests.get(url_daejeon, verify=False)
    soup_daejeon = BeautifulSoup(req_daejeon.content, 'html.parser')
    
    p_idx = [int(aa.text.replace('\n','')) for aa in soup_daejeon.select('tbody > tr > td')[::7]]
    c_date = [aa.text.replace('\n','').split('.')[0].zfill(2)+'-'+aa.text.replace('\n','').split('.')[1].replace('\xa0','').replace(' ','').zfill(2) for aa in soup_daejeon.select('tbody > tr > td')[2::7]]
    SGG = [aa.text.replace('\n','').replace('\xa0','') for aa in soup_daejeon.select('tbody > tr > td')[4::7]]

    new_result = pd.DataFrame({'p_idx':p_idx,'c_date':c_date, 'SGG':SGG})
    new_result.p_idx = new_result.p_idx.astype(int)
    new_result.c_date = '2021-'+new_result.c_date
    new_result.SGG = '대전 '+new_result.SGG
        
    return bring_2months('daejeon', new_result)


#### for Ulsan
def dataUpdate_ulsan():
    
    url_ulsan = 'https://covid19.ulsan.go.kr/index.do?showCnt=100'
    req_ulsan = requests.get(url_ulsan)
    soup_ulsan = BeautifulSoup(req_ulsan.content, 'html.parser')

    table = [aa.text for aa in soup_ulsan.select('table')[-1].select('tbody > tr > td') if len(aa.attrs)!=2]

    p_idx = [int(bb.replace('울산#','')) for bb in table[::5]]
    c_date = [bb.replace('/','-') for bb in table[3::5]]
    SGG = table[1::5]
    t_path = table[2::5]
    
    new_result = pd.DataFrame({'p_idx':p_idx,'c_date':c_date, 'SGG':SGG, 'origin':t_path})
    new_result.SGG = '울산 '+new_result.SGG
    new_result = new_result.sort_values(by='p_idx', ascending=False)

    return bring_2months('ulsan', new_result)


#### 
def confirmedCases_origin_30_days(pd_data, str_SGG, yyyy, mm, dd):
    
    file = pd_data
    
    day_30_list = [dt.datetime.strftime(dt.datetime(yyyy,mm,dd)-dt.timedelta(days=int(ii)), '%Y-%m-%d') for ii in np.arange(1,31)]
    file_day_30 = file[(file.c_date.isin(day_30_list))&(file.SGG==str_SGG)].copy()

    ###
    file_day_30_c = file_day_30.drop(['SGG'], axis=1).groupby(by=['c_date']).count().reset_index().sort_values(by='c_date', ascending=False)
    file_day_30_C = pd.merge(pd.DataFrame({'c_date':day_30_list}),file_day_30_c, how='left')
    file_day_30_C = file_day_30_C.fillna(0)
    confirmed_Cases = [int(aa) for aa in file_day_30_C.p_idx.values]

    ###
    if '서울' in str_SGG.split(' ')[0]:
        t_list = Counter([aa.replace(' 관련','').split('(')[0] for aa in file_day_30.origin.values if '관련' in aa])
        t_keys_3 = list(dict(sorted(t_list.items(), key=lambda x:x[1], reverse=True)).keys())[:3]    

    elif '대구' in str_SGG.split(' ')[0]:
        t_list = Counter([bb.split(' 관련')[0] for bb in [item for sublist in [aa.split('/') for aa in file_day_30.origin.values] for item in sublist] if '관련' in bb])
        t_keys_3 = list(dict(sorted(t_list.items(), key=lambda x:x[1], reverse=True)).keys())[:3]  

    elif '광주' in str_SGG.split(' ')[0]:
        t_list = Counter([aa.replace(' 관련','').split('(')[0] for aa in file_day_30.origin.values if '관련' in aa])
        t_keys_3 = list(dict(sorted(t_list.items(), key=lambda x:x[1], reverse=True)).keys())[:3] 

    elif '울산' in str_SGG.split(' ')[0]:
        t_list = Counter([bb.split(' 관련')[0] for bb in [item for sublist in [aa.split(',') for aa in file_day_30.origin.values] for item in sublist] if '관련' in bb])
        t_keys_3 = list(dict(sorted(t_list.items(), key=lambda x:x[1], reverse=True)).keys())[:3]  
    
    else: t_keys_3 = []
        
    return confirmed_Cases, t_keys_3


#### 
def make_30_days_records(yyyy,mm,dd):
    
    dir_path = f'./static/archives'
    yyyy_str = str(yyyy); mm_str = str(mm).zfill(2); dd_str = str(dd).zfill(2)
    
    if os.path.isfile(dir_path+f'/{yyyy_str}{mm_str}{dd_str}.json') == True:
        return None
    
    else: 
        
        day_30_list_label = [dt.datetime.strftime(dt.datetime(yyyy,mm,dd)-dt.timedelta(days=int(ii)), '%Y.%m.%d') for ii in np.arange(1,31)]
        
        ###
        updated_by_SGG = {'Seoul': dataUpdate_seoul(), 
                          'Daegu': dataUpdate_daegu(),
                          'Gwangju': dataUpdate_gwangju(),
                          'Ulsan': dataUpdate_ulsan()} # , 'Incheon': dataUpdate_incheon(),'Daejeon': dataUpdate_daejeon(),'Busan': dataUpdate_busan(),
        
        ###
        day_30_list_c = [dt.datetime.strftime(dt.datetime(yyyy,mm,dd)-dt.timedelta(days=int(ii)), '%Y-%m-%d') for ii in np.arange(0,31)]
        startCreateDt = day_30_list_c[-1][:4]+day_30_list_c[-1][5:7]+day_30_list_c[-1][8:10]
        
        url = f'http://openapi.data.go.kr/openapi/service/rest/Covid19/getCovid19SidoInfStateJson?serviceKey=2t52ye5eVy%2FenbN2RzxWVtkLSp1k44J3m4PQslsjH1TA3WIEs1vyOlwcLv5TrlVL15QxJlfjwzNp77l8114wOA%3D%3D&startCreateDt={startCreateDt}'
        req = requests.get(url)
        soup = BeautifulSoup(req.content, 'html.parser')
        
        c_date = [aa.text[:10] for aa in soup.select('body > items > item > createDT')]
        cityNm = [aa.text for aa in soup.select('body > items > item > gubun')]
        confirmedNumber_acc = [int(aa.text) for aa in soup.select('body > items > item > defCnt')]
        deathNumber_acc = [int(aa.text) for aa in soup.select('body > items > item > deathCnt')]
        
        update_by_city = pd.DataFrame({'cityNm':cityNm, 'c_date':c_date, 
                                       'confirmedNumber_acc':confirmedNumber_acc, 'deathNumber_acc':deathNumber_acc})
        
        for i_idx, ii in enumerate(update_by_city.cityNm.unique()):
            
            temp = update_by_city[update_by_city.cityNm==ii].copy().sort_values(by='c_date', ascending=False)
            temp['confirmedNumber'] = [temp.confirmedNumber_acc.values[ii] - temp.confirmedNumber_acc.values[ii+1] for ii in np.arange(30)] + [0]
            temp['deathNumber'] = [temp.deathNumber_acc.values[ii] - temp.deathNumber_acc.values[ii+1] for ii in np.arange(30)] + [0]
            
            if i_idx == 0:
                Temp = temp
            else:
                Temp = pd.concat([Temp, temp], ignore_index=True)
            
        update_by_city = Temp[Temp.c_date.isin(day_30_list_c[:-1])]        
        
        ###
        admin_dict_path = dir_path+'/SGG_dict.csv'
        admin_dict = pd.read_csv(admin_dict_path, encoding='euc-kr')
        
        json_file = {}
        
        json_file['date'] = day_30_list_label
                
        for a_kor, a_eng in admin_dict.loc[:,['name_Kor','name_Eng']].values:
            
            json_file[a_kor] = {}
            
            cityNm_eng = a_eng.split(' ')[0]; cityNm_kor = a_kor.split(' ')[0]
            
            if len(a_kor.split(' ')) > 1:
                
                SGG_confirmedNumber, SGG_origin =  confirmedCases_origin_30_days(updated_by_SGG[cityNm_eng], a_kor, yyyy, mm, dd)
                
                json_file[a_kor]['confirmedNumber'] = SGG_confirmedNumber
                if len(SGG_origin) > 0:
                    json_file[a_kor]['origin'] = SGG_origin
                else:
                    json_file[a_kor]['origin'] = ''
                                
            else: 
                
                json_file[a_kor]['confirmedNumber'] = [int(aa) for aa in update_by_city[update_by_city.cityNm==a_kor].sort_values(by='c_date', ascending=False).confirmedNumber.values]
                json_file[a_kor]['origin'] = ''
            
            json_file[a_kor]['deathNumber'] =[int(aa) for aa in update_by_city[update_by_city.cityNm==cityNm_kor].sort_values(by='c_date', ascending=False).deathNumber.values]
    
    ####
    output_file_path = dir_path+f'/{yyyy_str}{mm_str}{dd_str}.json'
    with open(output_file_path, 'w') as outfile:
        json.dump(json_file, outfile)
        
    return None


