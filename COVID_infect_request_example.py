import requests,xmltodict
import urllib.parse

# data with ad_district
serviceurl = 'http://openapi.data.go.kr/openapi/service/rest/Covid19/getCovid19SidoInfStateJson?serviceKey=2t52ye5eVy%2FenbN2RzxWVtkLSp1k44J3m4PQslsjH1TA3WIEs1vyOlwcLv5TrlVL15QxJlfjwzNp77l8114wOA%3D%3D'
params ={'pageNo' : '1',
 'numOfRows' : '10',
 'startCreateDt' : '20201010',
 'endCreateDt' : '20201110' }
resp = requests.get(serviceurl,params=params)
dictdata = xmltodict.parse(resp.content)
dictdata['response']['body']['items']['item']
# International immigrants
foreignurl = 'http://openapi.data.go.kr/openapi/service/rest/Covid19/getCovid19NatInfStateJson?serviceKey=2t52ye5eVy%2FenbN2RzxWVtkLSp1k44J3m4PQslsjH1TA3WIEs1vyOlwcLv5TrlVL15QxJlfjwzNp77l8114wOA%3D%3D'
params ={'pageNo' : '1',
 'numOfRows' : '10',
 'startCreateDt' : '20201010',
 'endCreateDt' : '20201110' }
resp = requests.get(foreignurl,params=params)
dictdata = xmltodict.parse(resp.content)
dictdata['response']['body']['items']['item']
# Genage
genageurl = 'http://openapi.data.go.kr/openapi/service/rest/Covid19/getCovid19GenAgeCaseInfJson?serviceKey=2t52ye5eVy%2FenbN2RzxWVtkLSp1k44J3m4PQslsjH1TA3WIEs1vyOlwcLv5TrlVL15QxJlfjwzNp77l8114wOA%3D%3D'
params ={'pageNo' : '1',
 'numOfRows' : '10',
 'startCreateDt' : '20201010',
 'endCreateDt' : '20201110' }
resp = requests.get(genageurl,params=params)
dictdata = xmltodict.parse(resp.content)
dictdata['response']['body']['items']['item']
# Covid infection now
covidurl = 'http://openapi.data.go.kr/openapi/service/rest/Covid19/getCovid19InfStateJson?serviceKey=2t52ye5eVy%2FenbN2RzxWVtkLSp1k44J3m4PQslsjH1TA3WIEs1vyOlwcLv5TrlVL15QxJlfjwzNp77l8114wOA%3D%3D'
params ={'pageNo' : '1',
 'numOfRows' : '10',
 'startCreateDt' : '20201010',
 'endCreateDt' : '20201110' }
resp = requests.get(covidurl,params=params)
dictdata = xmltodict.parse(resp.content)
dictdata['response']['body']['items']['item']
